import pymatching


def create_mwpm_decoder(circuit):
    """
    Create an MWPM decoder from a Stim surface-code circuit.
    """

    detector_error_model = circuit.detector_error_model(
        decompose_errors=True
    )

    matching = pymatching.Matching.from_detector_error_model(
        detector_error_model
    )

    return matching