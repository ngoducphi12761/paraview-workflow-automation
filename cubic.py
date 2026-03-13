import numpy as np
import matplotlib.pyplot as plt
# # Create sample data points (only four for a unique cubic solution)
# x = np.array([7.302837157, 7.076040972, 6.441011654, 6.214215469])
# y = np.array([0, 381, 1447, 2437])

# # Use numpy.polyfit to find the cubic coefficients (degree=3)
# # The coefficients are returned in order of highest degree to lowest (c3, c2, c1, c0)
# coeffs = np.polyfit(x, y, 3)

# # Unpack and print the coefficients
# c3, c2, c1, c0 = coeffs
# print(f"The coefficients are: c3={c3}, c2={c2}, c1={c1}, c0={c0}")
# # Output: The coefficients are: c3=0.8333333333333333, c2=-4.5, c1=6.666666666666666, c0=1.0

# mdot	        dP
# kg/s	        Pa
# 0.019335687	0
# 0.01876699	381
# 0.0170609	    1447
# 0.016492203	2437
# 0.015923507	2771
# 0.013080023	3561
# 0.009667843	4215
# 0.00682436	4992

# ============================================
# Input data: Mass flow rate (Q) and ΔP (Pa)
# ============================================
Q = np.array([
    0.019335687,
    0.01876699,
    0.0170609,
    0.016492203,
    0.015923507,
    0.013080023,
    0.009667843,
    0.00682436
])  # kg/s

dP = np.array([
    0,
    381,
    1447,
    2437,
    2771,
    3561,
    4215,
    4992
])  # Pa

# ============================================
# Polynomial fitting (degree = 3)
# ============================================
degree = 7 #3
coeffs2 = np.polyfit(Q, dP, degree)  # Returns [a3, a2, a1, a0]
print("Polynomial coefficients (highest power first):")
#c3, c2, c1, c0 = coeffs2
c7, c6, c5, c4, c3, c2, c1, c0 = coeffs2
# c7, c6, c5, c4, c3, c2, c1, c0 = coeffs2
print(f"The coefficients are: c7={c7}, c6={c6}, c5={c5}, c4={c4}, c3={c3}, c2={c2}, c1={c1}, c0={c0}")
#print(f"The coefficients are: c3={c3}, c2={c2}, c1={c1}, c0={c0}")