import stim

from src.noise.iid_noise import get_iid_noise, get_iid_noise_rates


def create_surface_code(
    distance: int,
    rounds: int,
    error_rate: float = 0.0,
    noise_components=None,
    noise_rates=None,
):
    """
    Create a rotated surface-code memory circuit using Stim.
    """

    if distance < 3 or distance % 2 == 0:
        raise ValueError("distance must be an odd integer >= 3")
    if rounds < 1:
        raise ValueError("rounds must be a positive integer")

    if noise_rates is None:
        noise = get_iid_noise(error_rate, components=noise_components)
    else:
        noise = get_iid_noise_rates(
            gate_error_rate=noise_rates.get("gate", error_rate),
            measurement_error_rate=noise_rates.get("measurement", error_rate),
            reset_error_rate=noise_rates.get("reset", error_rate),
            components=noise_components,
        )

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=rounds,
        **noise,
    )

    return circuit
