from src.circuits.surface_code import create_surface_code
from src.decoders.mwpm import create_mwpm_decoder


def test_surface_code_can_create_mwpm_decoder():
    circuit = create_surface_code(distance=3, rounds=3, error_rate=0.001)
    decoder = create_mwpm_decoder(circuit)

    assert circuit.num_detectors > 0
    assert decoder.num_detectors == circuit.num_detectors
