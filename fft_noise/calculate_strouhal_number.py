import sys
import numpy as np

L = 0.019          # m
U = 68.6           # m/s
T_START = 2.0      # s
T_END = 9.99995    # s

def compute_frequency(file_path, t_start=T_START, t_end=T_END):
    # Columns in liftDrag.dat:
    # 0 time, 1 totalLift, 2 frontLift, 3 rearLift, 4 drag, ...
    data = np.loadtxt(file_path, comments="#")

    t = data[:, 0]
    total_lift = data[:, 1]

    # Keep only 2.0 <= time <= 9.99995
    mask = (t >= t_start) & (t <= t_end)
    t = t[mask]
    total_lift = total_lift[mask]

    if len(t) < 10:
        raise ValueError("Not enough samples in the selected time range.")

    # Use average timestep in case of tiny floating-point variation
    dt = np.mean(np.diff(t))

    # Remove mean
    signal = total_lift - np.mean(total_lift)

    # Apply Hann window to reduce spectral leakage
    window = np.hanning(len(signal))
    signal = signal * window

    # FFT for real-valued signal
    fft_vals = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), d=dt)

    # Ignore zero frequency
    amplitudes = np.abs(fft_vals)
    amplitudes[0] = 0.0

    # Dominant frequency
    idx = np.argmax(amplitudes)
    f = freqs[idx]

    return f

def compute_strouhal(f, L=L, U=U):
    return f * L / U

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_strouhal_number.py path-to-liftDrag.dat")
        sys.exit(1)

    file_path = sys.argv[1]

    f = compute_frequency(file_path)
    st = compute_strouhal(f)

    print(f"Time window used: {T_START:.5f} to {T_END:.5f} s")
    print(f"Dominant frequency from totalLift: {f:.6f} Hz")
    print(f"Strouhal number: {st:.6f}")
