import stim

from src.noise.iid_noise import get_iid_noise


def create_surface_code(distance: int, rounds: int, error_rate: float = 0.0, noise_components=None):
    """
    Create a rotated surface-code memory circuit using Stim.
    """

    if distance < 3 or distance % 2 == 0:
        raise ValueError("distance must be an odd integer >= 3")
    if rounds < 1:
        raise ValueError("rounds must be a positive integer")

    noise = get_iid_noise(error_rate, components=noise_components)

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_z",
        distance=distance,
        rounds=rounds,
        **noise,
    )

    return circuit
