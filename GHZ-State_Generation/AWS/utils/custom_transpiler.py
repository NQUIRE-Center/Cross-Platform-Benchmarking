
import json
import math
import re
import networkx as nx


def build_cepheus_calibration_graph(calib_data, total_qubits=108):
    """Grafo de Cepheus ponderado por errores de calibración."""

    if isinstance(calib_data, str):
        calib_data = json.loads(calib_data)

    standardized = calib_data.get("standardized", {})
    one_q = standardized.get("oneQubitProperties", {})
    two_q = standardized.get("twoQubitProperties", {})

    G = nx.Graph()

    def get_fidelity(entries, preferred_gate=None):
        if not entries:
            return None

        selected = next(
            (x for x in entries
             if x.get("gateName") == preferred_gate),
            None,
        ) if preferred_gate else None

        if selected is None:
            selected = entries[0]

        fidelity = selected.get("fidelity")
        if fidelity is None:
            return None

        fidelity = float(fidelity)
        return fidelity if 0 < fidelity <= 1 else None

    # Solo añadimos qubits con calibración de una puerta.
    for key, data in one_q.items():
        match = re.search(r"\d+", str(key))
        if not match:
            continue

        q = int(match.group())
        if not 0 <= q < total_qubits:
            continue

        fidelity = get_fidelity(data.get("oneQubitFidelity"))
        if fidelity is None:
            continue

        G.add_node(
            q,
            fidelity=fidelity,
            error=1.0 - fidelity,
        )

    # Solo añadimos conexiones reales con fidelidad CZ conocida.
    for key, data in two_q.items():
        ids = re.findall(r"\d+", str(key))
        if len(ids) != 2:
            continue

        u, v = map(int, ids)
        if u not in G or v not in G:
            continue

        fidelity = get_fidelity(
            data.get("twoQubitGateFidelity"),
            preferred_gate="CZ",
        )
        if fidelity is None:
            continue

        # Coste aproximado de error acumulado.
        error_u = G.nodes[u]["error"]
        error_v = G.nodes[v]["error"]
        error_edge = 1.0 - fidelity

        cost = (
            -math.log(fidelity)
            -math.log(G.nodes[u]["fidelity"])
            -math.log(G.nodes[v]["fidelity"])
        )

        G.add_edge(
            u, v,
            fidelity=fidelity,
            error=error_edge,
            weight=cost,
        )

    return G

def find_best_physical_chain(
    graph,
    num_qubits,
    single_qubit_weight=0.25,
):
    """
    Busca una cadena simple de num_qubits nodos.

    El coste combina errores de los qubits y de las conexiones.
    Requiere que las calibraciones estén disponibles en el grafo.
    """
    if num_qubits < 1:
        raise ValueError("num_qubits debe ser >= 1")

    if num_qubits > graph.number_of_nodes():
        raise ValueError("No hay suficientes qubits calibrados")

    best_path = None
    best_cost = float("inf")

    def search(path, visited, cost):
        nonlocal best_path, best_cost

        if len(path) == num_qubits:
            if cost < best_cost:
                best_path = path.copy()
                best_cost = cost
            return

        if cost >= best_cost:
            return

        current = path[-1]

        for nxt in graph.neighbors(current):
            if nxt in visited:
                continue

            edge_cost = graph[current][nxt]["weight"]
            node_cost = (
                -math.log(graph.nodes[nxt]["fidelity"])
                * single_qubit_weight
            )

            new_cost = cost + edge_cost + node_cost

            if new_cost >= best_cost:
                continue

            visited.add(nxt)
            path.append(nxt)

            search(path, visited, new_cost)

            path.pop()
            visited.remove(nxt)

    for start in graph.nodes:
        initial_cost = (
            -math.log(graph.nodes[start]["fidelity"])
            * single_qubit_weight
        )
        search([start], {start}, initial_cost)

    if best_path is None:
        raise ValueError(
            f"No existe una cadena de {num_qubits} "
            "qubits en el grafo calibrado."
        )

    return best_path, best_cost