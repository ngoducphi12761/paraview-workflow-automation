#!/usr/bin/env python3
import sys
import argparse
import numpy as np
from scipy.fft import fft, fftfreq

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Extract time window and calculate Strouhal using scipy.fft")
    parser.add_argument("filepath", help="Path to the liftDrag.dat file")
    
    # Time window defaults
    parser.add_argument("--tmin", type=float, default=2.0, help="Minimum time (default: 2.0)")
    parser.add_argument("--tmax", type=float, default=9.99995, help="Maximum time (default: 9.99995)")
    
    # Physics parameters defaults
    parser.add_argument("--L", type=float, default=0.019, help="Characteristic length in meters (default: 0.019)")
    parser.add_argument("--U", type=float, default=68.6, help="Free-stream velocity in m/s (default: 68.6)")

    args = parser.parse_args()

    # 1. Load data, ignoring header lines starting with '#'
    try:
        data = np.loadtxt(args.filepath, comments='#')
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # 2. Extract Time and totalLift
    time = data[:, 0]
    total_lift = data[:, 1]

    # 3. Create a mask and filter for the specific time window
    mask = (time >= args.tmin) & (time <= args.tmax)
    t_slice = time[mask]
    lift_slice = total_lift[mask]

    if len(t_slice) < 2:
        print(f"Error: Not enough data points found between t = {args.tmin} and t = {args.tmax}.")
        sys.exit(1)

    # 4. Perform FFT using scipy.fft on the filtered slice
    n = len(t_slice)
    dt = np.mean(np.diff(t_slice))
    
    yf = fft(lift_slice)
    xf = fftfreq(n, dt)[:n//2]
    amplitudes = np.abs(yf[:n//2])

    # 5. Find dominant frequency (ignoring the 0 Hz DC offset)
    if len(amplitudes) > 1:
        amplitudes[0] = 0  
        idx = np.argmax(amplitudes)
        dominant_f = xf[idx]
    else:
        print("Error: FFT resulted in insufficient frequency bins.")
        sys.exit(1)

    # 6. Calculate Strouhal number
    St = (dominant_f * args.L) / args.U

    # 7. Print Output
    print("-" * 45)
    print("      WINDOWED FFT & STROUHAL ANALYSIS      ")
    print("-" * 45)
    print(f"File Processed : {args.filepath}")
    print(f"Time Window    : {t_slice[0]:.5f} to {t_slice[-1]:.5f} s")
    print(f"Data Points    : {n}")
    print(f"Average dt     : {dt:.6g} s")
    print("-" * 45)
    print(f"Dominant Freq  : {dominant_f:.2f} Hz")
    print(f"Strouhal (St)  : {St:.4f}")
    print("-" * 45)

if __name__ == "__main__":
    main()