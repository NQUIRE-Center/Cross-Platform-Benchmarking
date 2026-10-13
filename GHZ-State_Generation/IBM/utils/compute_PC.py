
import json
import numpy as np


def ideal_ghz_sign(observable):
    """
    Calculates the ideal sign of a GHZ+ stabilizer.

    I/Z subgroup: even number of Z -> sign +1.
    X/Y subgroup: all characters are X/Y and the number
    of Y is even -> sign (-1)**(n_y // 2).
    """
    observable = observable.upper()

    if not observable or any(c not in "IXYZ" for c in observable):
        raise ValueError(f"Invalid observable: {observable}")

    if all(c in "IZ" for c in observable):
        if observable.count("Z") % 2 != 0:
            raise ValueError(
                f"{observable} is not a valid GHZ+ stabilizer."
            )
        return 1

    if all(c in "XY" for c in observable):
        n_y = observable.count("Y")

        if n_y % 2 != 0:
            raise ValueError(
                f"{observable} is not a valid GHZ+ stabilizer."
            )

        return (-1) ** (n_y // 2)

    raise ValueError(
        f"{observable} does not belong to the stabilizer group "
        "of the standard GHZ+."
    )


def calculate_metrics(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    observables = data["observables"]
    expected_values = data["expected_values"]

    if len(observables) != len(expected_values):
        raise ValueError(
            "observables and expected_values must have the same length."
        )

    # N is obtained from the field indicated in the JSON
    N = data["numero_qubits_inicial"]

    # Pairs are kept, including duplicates
    group_X = []
    group_Z = []

    for obs, expected in zip(observables, expected_values):
        obs = obs.upper()
        pair = (obs, float(expected))

        if any(c in obs for c in "XY"):
            group_X.append(pair)
        else:
            group_Z.append(pair)

    def calculate_mu(group):
        if not group:
            raise ValueError(
                "There are no observables in one of the groups."
            )

        values = np.array([expected for obs, expected in group])

        signs = np.array([
            ideal_ghz_sign(obs) for obs, expected in group
        ])

        if not np.all(np.isfinite(values)):
            raise ValueError("There are non-finite expected_values.")

        mu = np.mean(values * signs)
        return mu, signs

    mu_X, signs_X = calculate_mu(group_X)
    mu_Z, signs_Z = calculate_mu(group_Z)

    P_hat = (
        1 + (2 ** (N - 1) - 1) * mu_Z
    ) / (2 ** (N - 1))

    C_hat = mu_X

    return {
        "N": N,
        "n_observables_X": len(group_X),
        "n_observables_Z": len(group_Z),
        "mu_X": mu_X,
        "mu_Z": mu_Z,
        "P_hat": P_hat,
        "C_hat": C_hat,
        "grupo_X": group_X,
        "grupo_Z": group_Z,
        "signos_X": signs_X,
        "signos_Z": signs_Z,
    }


if __name__ == "__main__":

    results = calculate_metrics(r'.\qmio_GHZ\experiment_results\results_qmio_8q_20260722_151956.json')

    for key in [
        "N",
        "n_observables_X",
        "n_observables_Z",
        "mu_X",
        "mu_Z",
        "P_hat",
        "C_hat",
    ]:
        print(f"{key}: {results[key]:.10f}"
              if isinstance(results[key], (float, np.floating))
              else f"{key}: {results[key]}")