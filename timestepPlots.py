import re
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

def parse_log_file(log_file):
    iterations = []
    times = []
    deltaTs = []

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        iter_count = 0
        for line in f:
            # Match total simulation time
            time_match = re.search(r'\b[Tt]ime\s*=\s*([0-9eE\+\-\.]+)', line)
            if time_match:
                iter_count += 1
                times.append(float(time_match.group(1)))
                iterations.append(iter_count)
                continue

            # Match deltaT value
            dt_match = re.search(r'\bdeltaT\s*=\s*([0-9eE\+\-\.]+)', line)
            if dt_match:
                deltaTs.append(float(dt_match.group(1)))

    return np.array(iterations), np.array(times), np.array(deltaTs)


def plot_deltaT(iterations, deltaTs, log_file, skip_first=1000):
    # Align lengths
    n = min(len(iterations), len(deltaTs))
    iterations = iterations[:n]
    deltaTs = deltaTs[:n]

    # Skip the first few iterations
    if len(iterations) > skip_first:
        iterations = iterations[skip_first:]
        deltaTs = deltaTs[skip_first:]
    else:
        print(f"Log has fewer than {skip_first} entries; using all data instead.\n")

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, deltaTs, color='tab:red', linewidth=1.2)
    plt.xlabel("Iteration Number", fontsize=12)
    plt.ylabel("deltaT (s)", fontsize=12, color='tab:red')
    plt.title(f"deltaT vs Iteration (after {skip_first})\n{os.path.basename(log_file)}", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Save plot cross-platform
    output_file = os.path.join(os.getcwd(), "deltaT_vs_iteration.png")
    plt.savefig(output_file, dpi=300)
    print(f"\nFigure saved as '{output_file}'\n")

    plt.show()

    return deltaTs


def main():
    if len(sys.argv) < 2:
        print("Usage: py timestepPlots.py <logfile>")
        sys.exit(1)

    log_file = os.path.abspath(sys.argv[1])
    if not os.path.isfile(log_file):
        print(f"Log file not found: {log_file}")
        sys.exit(1)

    iterations, times, deltaTs = parse_log_file(log_file)

    if len(deltaTs) == 0:
        print("No 'deltaT =' entries found in the log file.")
        sys.exit(1)

    # Plot and get filtered deltaT
    filtered_deltaTs = plot_deltaT(iterations, deltaTs, log_file, skip_first=1000)

    # Δt statistics for filtered data
    avg_dt = np.mean(filtered_deltaTs)
    min_dt = np.min(filtered_deltaTs)
    max_dt = np.max(filtered_deltaTs)

    print(f"Average Δt (after 1000) = {avg_dt:.3e} s")
    print(f"Minimum Δt (after 1000) = {min_dt:.3e} s")
    print(f"Maximum Δt (after 1000) = {max_dt:.3e} s\n")


if __name__ == "__main__":
    main()
