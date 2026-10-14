import numpy as np
import yaml

from datetime import datetime

from utils.aws_benchmark import required_shots_witnesses, run_GHZ_Witnesses_experiment, sample_ghz_stabilizer, observable_from_string, compute_l, run_GHZ_RF_experiment
from utils.aws_circuits import create_ghz_circuit
from utils.custom_transpiler import build_cepheus_calibration_graph, find_best_physical_chain

from braket.aws import AwsDevice
#from QCentroidLoaders import BraketLoader

import logging

#logger = logging.getLogger("qcentroid-user-log")

class GHZExperiment():
    def __init__(self, num_qubits, circuit, l, m_i, backend, min_shots=1, custom_transpiler=False, qpu_size=0):
        """
        Docstring for __init__
        :param num_qubits: Number of qubits in the GHZ state
        :param circuit: QuantumCircuit that prepares the GHZ state
        :param l: Parameter for the experiment
        :param m_i: Number of shots for the experiment
        :param backend: Backend for running the experiment
        :param custom_transpiler: Whether to use a custom transpiler
        """ 
        self.num_qubits = num_qubits
        self.circuit = circuit[0]
        self.path = circuit[1]
        self.qpu_size = qpu_size
        self.l = l
        self.m_i = m_i
        self.backend = backend
        self.min_shots = min_shots
        self.custom_transpiler = custom_transpiler
    def prepare_experiment(self):

        samples = sample_ghz_stabilizer(self.num_qubits, self.l)
        if self.custom_transpiler:
            # Use self.path to transpile the observables to the physical qubits
            identity = self.qpu_size*'I'
            for sample in samples:
                p, sign = sample
                new_p = list(identity)
                for i, qubit in enumerate(self.path):
                    new_p[qubit] = p[i]
                sample[0] = ''.join(new_p)

        observables = [observable_from_string(p) for (p, _) in samples]
        signs = np.array([sign for (_, sign) in samples])

        self.observables = observables
        self.signs = signs
        
    def run_experiment(self):
        return run_GHZ_RF_experiment(circuit=self.circuit, num_qubits=self.num_qubits, observables=self.observables, signs=self.signs, backend=self.backend, min_shots=self.min_shots)

def getBestGHZCircuitsPerQPU(backend_architecture, start_qubits=2, max_qubits=2, native_gates=False, graph=None):
    """
    Transpiles and selects the best circuits according to the backend calibration.

    Args:
        backend_architecture (str): Backend architecture, which can be "lineal" or "fully-connected"
        start_qubits (int): Starting number of qubits
        max_qubits (int): Maximum number of qubits
        native_gates (bool): Whether to use native gates

    Returns:
        List[QuantumCircuit]: Optimized transpiled circuits
    """
    if native_gates:
        best_strategy = "native"
    else:
        if backend_architecture == "lineal":
            best_strategy = "lineal_v2"
        elif backend_architecture == "fully-connected":
            best_strategy = "log_v2"

    circuits = {}

    for i in range(start_qubits, max_qubits+1):
        path, cost = find_best_physical_chain(
            graph,
            num_qubits=i,
        )
        circuits[i] = [create_ghz_circuit(i, mode=best_strategy, path=path), path]

    return circuits

def runExperiments(backend_arn, backend_architecture, smaller_size, max_qubits, epsilon, delta, min_shots=1, custom_transpiler=False):
    # Log the start of the experiment (backend, qubits, epsilon, delta)
    #logger.info(f"Backend: {backend_arn}, Qubits: {smaller_size}, Epsilon: {epsilon}, Delta: {delta}")
    print(f"Backend: {backend_arn}, Qubits: {smaller_size}, Epsilon: {epsilon}, Delta: {delta}")
    backend = AwsDevice(backend_arn)
    #backend = BraketLoader.get_target()
    backend_properties = backend.properties
    qpu_size = backend_properties.paradigm.qubitCount


    start_date = datetime.now()
    start_date_str = start_date.strftime("%Y%m%d_%H%M%S")

    if custom_transpiler:
        graph = build_cepheus_calibration_graph(
            backend_properties,
            total_qubits=max_qubits,
        )
    else:
        graph = None

    best_circuits = getBestGHZCircuitsPerQPU(backend_architecture=backend_architecture, start_qubits=smaller_size, max_qubits=max_qubits, native_gates=custom_transpiler, graph=graph)

    experiments = {}
    for num_qubits in range(smaller_size, max_qubits + 1):
        # Save the circuit
        circuit = best_circuits[num_qubits]
        
        l = compute_l(epsilon, delta)
        m_i = None # m_i is not needed for the RF benchmark, but we keep it as a parameter for simplicity
        experiment = GHZExperiment(num_qubits, circuit, l, m_i, backend, min_shots=min_shots, custom_transpiler=custom_transpiler, qpu_size=qpu_size)
        experiment.prepare_experiment()
        experiments[num_qubits] = experiment
    
    num_qubits = smaller_size - 1
    results_to_save = []

    try:
        max_idx = max_qubits
        min_idx = smaller_size
        idx = int((max_idx+min_idx) // 2)
        end = False

        while not end:
            experiment = experiments[idx]
            try:
                # Run the GHZ experiment
                result = experiment.run_experiment()

                num_qubits = experiment.num_qubits
                fidelity_estimate, metadata = result

                results_to_save.append(
                    (num_qubits, fidelity_estimate, metadata)
                )

                if fidelity_estimate < (1 / 2 - epsilon):
                    # If the fidelity is below the threshold discard the upper half of the search space
                    max_idx = idx - 1
                    if min_idx > max_idx:
                        #logger.info(
                        #    f"Fidelity estimate {fidelity_estimate} crosses threshold at {idx} qubits. Stopping further experiments."
                        #)
                        print(
                            f"Fidelity estimate {fidelity_estimate} crosses threshold at {idx} qubits. Stopping further experiments."
                        )
                        end = True
                    else:
                        idx = int((max_idx+min_idx) // 2)
                else:
                    # If the fidelity is above the threshold discard the lower half of the search space
                    min_idx = idx + 1
                    if min_idx > max_idx:
                        #logger.info(
                        #    f"Fidelity estimate {fidelity_estimate} crosses threshold at {idx+1} qubits. Stopping further experiments."
                        #)
                        print(
                            f"Fidelity estimate {fidelity_estimate} crosses threshold at {idx+1} qubits. Stopping further experiments."
                        )
                        end = True
                    else:
                        idx = int((max_idx+min_idx) // 2)


            except Exception as exp_err:
                #logger.error(f"Error during experiment execution: {exp_err}")
                print(f"Error during experiment execution: {exp_err}")
                end = True  # stop further experiments but still save results

    except Exception as session_err:
        #logger.error(f"Session-level error occurred: {session_err}")
        print(f"Session-level error occurred: {session_err}")

    finally:
        # ALWAYS save whatever results we have
        result_dict = {
            "backend": backend_arn,
        }
        for results in results_to_save:
            num_qubits, fidelity_estimate, metadata = results
            result_dict[f"{num_qubits}_qubits"] = {
                "fidelity_estimate": fidelity_estimate,
                "epsilon": epsilon,
                "delta": delta,
                "metadata": metadata,
            }
        result_dict["properties"] = backend_properties.json()
        result_dict["date"] = start_date_str
    return result_dict
    

def run(input_data:dict, solver_params:dict, extra_arguments:dict) -> dict:
    backend_arn = input_data.get("backend_arn")
    backend_architecture = input_data.get("backend_architecture")
    start_size = input_data.get("start_size")
    max_size = input_data.get("max_size")
    epsilon = input_data.get("epsilon")
    delta = input_data.get("delta")
    min_shots = input_data.get("min_shots", 1)

    return runExperiments(backend_arn, backend_architecture, start_size, max_size, epsilon, delta, min_shots=min_shots)

if __name__ == "__main__":
    # get input_data from \experiment_definitions\real_cepheus.yml

    with open("experiment_definitions/real_cepheus.yml", "r") as f:
        config = yaml.safe_load(f)
    input_data = config["experiments"][0]["params"]
    solver_params = {}
    extra_arguments = {}

    results = run(input_data, solver_params, extra_arguments)
    print(results)