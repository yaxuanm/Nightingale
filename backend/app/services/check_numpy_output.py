import numpy as np
arr = np.load("debug_output.npy")
print("Shape:", arr.shape)
print("Dtype:", arr.dtype)
print("Min:", arr.min())
print("Max:", arr.max()) 