import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def read_input_file(input_file):
    params = {}

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#") or line.startswith("//"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.split("#", 1)[0].strip()
            value = value.split("//", 1)[0].strip()
            params[key.strip()] = value

    required = [
        "file_path",
        "t_min",
        "t_max",
        "st_min",
        "st_max",
        "sample_step",
        "D",
        "U_inf",
        "p_ref",
        "base_dt",
    ]

    missing = [key for key in required if key not in params]
    if missing:
        raise ValueError(f"Missing keys in input file: {', '.join(missing)}")

    return {
        "file_path": params["file_path"],
        "t_min": float(params["t_min"]),
        "t_max": float(params["t_max"]),
        "st_min": float(params["st_min"]),
        "st_max": float(params["st_max"]),
        "sample_step": int(params["sample_step"]),
        "D": float(params["D"]),
        "U_inf": float(params["U_inf"]),
        "p_ref": float(params["p_ref"]),
        "base_dt": float(params["base_dt"]),
        "smooth_window": int(params.get("smooth_window", "200")),
        "output_png": params.get("output_png", "spl_vs_strouhal.png"),
        "output_dat": params.get("output_dat", "SPLversusStrouhalnumber.dat"),
        "output_smooth_dat": params.get("output_smooth_dat", "SPLversusStrouhalnumber_smoothed.dat"),
    }


def read_fwh_file(file_path):
    file_path = Path(file_path)

    times = []
    pressures = []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            try:
                t = float(parts[0])
                p = float(parts[2])
            except ValueError:
                continue

            times.append(t)
            pressures.append(p)

    if len(times) < 2:
        raise ValueError("Not enough numeric data found in file.")

    return np.array(times, dtype=float), np.array(pressures, dtype=float)


def compute_spl_spectrum(p, dt, p_ref):
    fs = 1.0 / dt
    n = len(p)

    p_fluc = p - np.mean(p)

    window = np.hanning(n)
    coherent_gain = np.mean(window)
    p_win = p_fluc * window

    fft_vals = np.fft.rfft(p_win)
    freq = np.fft.rfftfreq(n, d=dt)

    amp_peak = (2.0 / (n * coherent_gain)) * np.abs(fft_vals)

    amp_peak[0] /= 2.0
    if n % 2 == 0 and len(amp_peak) > 1:
        amp_peak[-1] /= 2.0

    amp_rms = amp_peak / np.sqrt(2.0)

    eps = 1e-30
    spl = 20.0 * np.log10(np.maximum(amp_rms, eps) / p_ref)

    return freq, spl, amp_rms, fs


def frequency_to_strouhal(freq, diameter, u_inf):
    return freq * diameter / u_inf


def moving_average(x, window):
    if window <= 1:
        return x.copy()
    if window > len(x):
        window = len(x)
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(x, kernel, mode="same")


def analyze_from_config(config):
    file_path = Path(config["file_path"])
    t_min = config["t_min"]
    t_max = config["t_max"]
    st_min = config["st_min"]
    st_max = config["st_max"]
    sample_step = config["sample_step"]
    diameter = config["D"]
    u_inf = config["U_inf"]
    p_ref = config["p_ref"]
    base_dt = config["base_dt"]
    smooth_window = config["smooth_window"]
    output_png = config["output_png"]
    output_dat = config["output_dat"]
    output_smooth_dat = config["output_smooth_dat"]

    t, p = read_fwh_file(file_path)

    time_mask = (t >= t_min) & (t <= t_max)
    t = t[time_mask]
    p = p[time_mask]

    if len(t) < 2:
        raise ValueError("Not enough samples in selected time window.")

    t = t[::sample_step]
    p = p[::sample_step]

    if len(t) < 2:
        raise ValueError("Not enough samples after sampling step.")

    dt_eff = base_dt * sample_step

    freq, spl, amp_rms, fs = compute_spl_spectrum(p, dt_eff, p_ref)
    st = frequency_to_strouhal(freq, diameter, u_inf)

    mask = (st >= st_min) & (st <= st_max) & (freq > 0.0)
    if not np.any(mask):
        raise ValueError("No points found in requested Strouhal range.")

    freq_sel = freq[mask]
    st_sel = st[mask]
    spl_sel = spl[mask]
    amp_sel = amp_rms[mask]

    # Smooth only for plotting and peak picking
    spl_smooth = moving_average(spl_sel, smooth_window)

    i_peak = np.argmax(spl_smooth)
    f_peak = freq_sel[i_peak]
    st_peak = st_sel[i_peak]
    spl_peak = spl_smooth[i_peak]

    output_png_path = file_path.parent / output_png
    output_dat_path = file_path.parent / output_dat
    output_smooth_dat_path = file_path.parent / output_smooth_dat

    raw_data = np.column_stack((freq_sel, st_sel, spl_sel, amp_sel))
    np.savetxt(
        output_dat_path,
        raw_data,
        fmt="%.8e",
        header="frequency_Hz Strouhal SPL_dB_raw p_rms_Pa",
        comments=""
    )

    smooth_data = np.column_stack((freq_sel, st_sel, spl_smooth))
    np.savetxt(
        output_smooth_dat_path,
        smooth_data,
        fmt="%.8e",
        header="frequency_Hz Strouhal SPL_dB_smoothed",
        comments=""
    )

    plt.figure(figsize=(10, 6))
    plt.plot(st_sel, spl_sel, linewidth=0.6, alpha=0.35, label="Raw SPL")
    plt.plot(st_sel, spl_smooth, linewidth=2.0, color="black", label="Smoothed SPL")
    plt.scatter([st_peak], [spl_peak], color="red", s=90, label=f"Peak St = {st_peak:.5f}")
    plt.xlabel("Strouhal Number")
    plt.ylabel("SPL (dB)")
    plt.title(f"SPL vs Strouhal Number ({t_min:.5f} s to {t_max:.5f} s, every {sample_step}th sample)")
    plt.xlim(st_min, st_max)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=300)
    plt.close()

    print(f"Input file: {file_path}")
    print(f"Selected {len(t)} samples")
    print(f"Time window used: {t_min:.5f} to {t_max:.5f} s")
    print(f"Sampling step: every {sample_step}th row")
    print(f"Effective dt: {dt_eff:.8f} s")
    print(f"Sampling frequency: {fs:.3f} Hz")
    print(f"Smoothing window: {smooth_window} points")
    print(f"Dominant peak from smoothed spectrum: f = {f_peak:.3f} Hz, St = {st_peak:.5f}, SPL = {spl_peak:.3f} dB")
    print(f"Saved raw data to: {output_dat_path}")
    print(f"Saved smoothed data to: {output_smooth_dat_path}")
    print(f"Saved plot to: {output_png_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 plot_SPL_Strouhal_number.py input.in")
        sys.exit(1)

    config = read_input_file(sys.argv[1])
    analyze_from_config(config)
