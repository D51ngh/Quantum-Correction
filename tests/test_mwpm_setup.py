from src.circuits.surface_code import create_surface_code
from src.decoders.mwpm import create_mwpm_decoder


circuit = create_surface_code(
    distance=3,
    rounds=3,
    error_rate=0.001
)

decoder = create_mwpm_decoder(circuit)

print("Circuit created successfully")
print("MWPM decoder created successfully")
print(decoder)