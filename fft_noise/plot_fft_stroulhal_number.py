import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DT = 0.00005

def analyze_lift(file_path, t_start, t_end, output_png="fft_totalLift.png", output_dat="fft_totalLift.dat"):
    file_path = Path(file_path)
    data = np.loadtxt(file_path, comments="#")

    # Columns:
    # 0 time, 1 totalLift, 2 frontLift, 3 rearLift, 4 drag, ...
    time = data[:, 0]
    total_lift = data[:, 1]

    # Apply requested time window
    mask = (time >= t_start) & (time <= t_end)
    time = time[mask]
    signal = total_lift[mask]

    if len(signal) < 2:
        raise ValueError("Not enough samples in selected time range.")

    # Remove mean
    signal = signal - np.mean(signal)

    n = len(signal)

    # Full FFT
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(n, DT)
    amplitudes = np.abs(yf) / n

    # Positive frequencies only for plotting and peak detection
    pos_mask = xf > 0
    xf_pos = xf[pos_mask]
    amp_pos = amplitudes[pos_mask]

    if len(xf_pos) == 0:
        raise ValueError("No positive frequencies found.")


    output_png_path = file_path.parent / output_png
    output_dat_path = file_path.parent / output_dat
  # Export frequency-amplitude data
    fft_data = np.column_stack((xf_pos, amp_pos))
    np.savetxt(
        output_dat_path,
        fft_data,
        fmt="%.8f",
        header="Frequency(Hz) totalLiftAmplitude",
        comments=""
    )

    idx = np.argmax(amp_pos)
    dominant_f = xf_pos[idx]
    dominant_amp = amp_pos[idx]

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(xf_pos, amp_pos, linewidth=1.0)
    plt.scatter([dominant_f], [dominant_amp], color="red", label=f"Peak = {dominant_f:.6f} Hz")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("totalLift Amplitude")
    plt.title(f"FFT of totalLift ({t_start} s to {t_end} s)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=300)
    plt.close()

    print(f"Time window used: {t_start:.5f} to {t_end:.5f} s")
    print(f"Samples used: {n}")
    print(f"Fixed timestep: {DT:.8f} s")
    print(f"Dominant frequency: {dominant_f:.6f} Hz")
    print(f"Amplitude at dominant frequency: {dominant_amp:.6e}")
    print(f"FFT plot saved to: {output_png_path}")
    print(f"FFT data saved to: {output_dat_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python plot_fft_totalLift.py path-to-liftDrag.dat T_START T_END [output.png]")
        sys.exit(1)

    file_path = sys.argv[1]
    t_start = float(sys.argv[2])
    t_end = float(sys.argv[3])
    output_png = sys.argv[4] if len(sys.argv) > 4 else "fft_totalLift.png"
    output_dat = sys.argv[5] if len(sys.argv) > 5 else "fft_totalLift.dat"
    analyze_lift(file_path, t_start, t_end, output_png, output_dat)
