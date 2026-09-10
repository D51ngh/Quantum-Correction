def get_iid_noise(error_rate: float):
    """
    Create independent (IID) noise settings.

    Parameters
    ----------
    error_rate : float
        Probability of a physical error.

    Returns
    -------
    dict
        Noise parameters that can be passed to Stim.
    """

    if not 0 <= error_rate <= 1:
        raise ValueError("error_rate must be between 0 and 1")

    noise = {
        "after_clifford_depolarization": error_rate,
        "before_measure_flip_probability": error_rate,
        "after_reset_flip_probability": error_rate,
    }

    return noise
