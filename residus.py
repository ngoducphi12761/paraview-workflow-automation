import re
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import argparse

def plot_residuals_minimal(log_file_path: str, output_image_path: str = 'residuals_plot_minimal.png'):
    """
    Parses an OpenFOAM/HELYX log file to extract and plot final residuals
    using only the re and matplotlib libraries.

    Args:
        log_file_path (str): The path to the log file (e.g., 'runCase.log').
        output_image_path (str): The path to save the output plot image.
    """
    print(f"Parsing log file: {log_file_path}")

    # Regex to find the time and the final residuals for the variables
    time_regex = re.compile(r'^Time = (\S+)')
    residual_regex = re.compile(r'Solving for (\w+),.*?Final residual = ([\d.eE+-]+)')

    data_rows = []
    current_time_step_data = {}

    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                time_match = time_regex.match(line)
                if time_match:
                    # A new time step begins. If we have data from the previous step,
                    # store it before starting a new one.
                    if current_time_step_data and len(current_time_step_data) > 1:
                        data_rows.append(current_time_step_data)
                    
                    # Start a new dictionary for the new time step
                    try:
                        time_val = float(time_match.group(1))
                        current_time_step_data = {'Time': time_val}
                    except ValueError:
                        # Skip if the time value is not a valid float
                        current_time_step_data = {}
                    continue

                residual_match = residual_regex.search(line)
                if residual_match and current_time_step_data:
                    variable = residual_match.group(1)
                    residual = float(residual_match.group(2))
                    # Store the final residual for the variable
                    current_time_step_data[variable] = residual

        # Append the very last collected time step data if it exists
        if current_time_step_data and len(current_time_step_data) > 1:
            data_rows.append(current_time_step_data)

    except FileNotFoundError:
        print(f"Error: Log file not found at '{log_file_path}'")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if not data_rows:
        print("No residual data found in the log file.")
        return

    # --- Structure data for plotting (replaces pandas.DataFrame) ---
    # Get all unique variable names found in the log
    all_vars = set()
    for row in data_rows:
        all_vars.update(row.keys())
    all_vars.discard('Time')  # We don't want to plot Time against itself
    
    # Initialize the plotting data structure
    plot_data = {var: [] for var in all_vars}
    plot_data['Time'] = []

    # Populate the lists, handling missing values with 'nan'
    for row in data_rows:
        plot_data['Time'].append(row.get('Time'))
        for var in all_vars:
            # Use .get() to provide a default value (nan) if the key is missing
            plot_data[var].append(row.get(var, float('nan')))

    # --- Plotting with Matplotlib only ---
    print("Generating plot...")
    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot each variable's residual history
    for var in sorted(list(all_vars)): # Sort for a consistent legend order
        ax.plot(plot_data['Time'], plot_data[var], marker='.', linestyle='-', label=var)

    # Formatting the plot
    ax.set_yscale('log')
    ax.set_xlabel('Simulation Time (s)', fontsize=12)
    ax.set_ylabel('Final Residual', fontsize=12)
    ax.set_title('Solver Final Residuals vs. Time', fontsize=16, fontweight='bold')
    
    ax.grid(True, which="both", linestyle='--', linewidth=0.5)
    ax.legend(title='Variables', bbox_to_anchor=(1.02, 1), loc='upper left')
    
    # Use a logarithmic locator for the y-axis for better tick placement
    ax.yaxis.set_major_locator(mticker.LogLocator(numticks=15))
    ax.yaxis.set_minor_locator(mticker.LogLocator(numticks=15, subs='auto'))

    plt.tight_layout(rect=[0, 0, 0.9, 1]) # Adjust layout to make room for legend
    
    # Save the figure
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_image_path}")
    plt.close(fig)


if __name__ == '__main__':
    # --- Setup command-line argument parsing for flexibility ---
    parser = argparse.ArgumentParser(
        description="Parse an OpenFOAM/HELYX log file and plot final residuals.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Default log file path constructed in an OS-agnostic way
    default_log_file = os.path.join('log', 'runCase.log')

    parser.add_argument(
        '--logfile',
        type=str,
        default=default_log_file,
        help="Path to the log file to be parsed."
    )
    parser.add_argument(
        '--output',
        type=str,
        default='residuals_plot.png',
        help="Path to save the output plot image."
    )
    args = parser.parse_args()
    
    # --- Execution ---
    plot_residuals_minimal(log_file_path=args.logfile, output_image_path=args.output)
