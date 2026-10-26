from collections import defaultdict
import csv
import sys


def parse_rtl_power(filepath):
  # Dictionary to group chunks by (date, time)
  # Key: (date, time), Value: list of tuples (global_min_freq, min_power)
  sweeps = defaultdict(list)

  try:
    with open(filepath, mode="r") as file:
      reader = csv.reader(file)
      for row in reader:
        if not row or len(row) < 7:
          continue

        date = row[0].strip()
        time = row[1].strip()
        start_freq = float(row[2])
        bin_size = float(row[4])

        power_values = [float(p) for p in row[6:]]
        if not power_values:
          continue

        # Find the minimum power and its index *within this specific chunk*
        min_power_idx = power_values.index(min(power_values))
        min_power = power_values[min_power_idx]

        # Calculate the absolute center frequency for this bin
        bin_frequency = start_freq + (min_power_idx + 0.5) * bin_size

        # Store this chunk's minimum found
        sweeps[(date, time)].append((bin_frequency, min_power))

  except FileNotFoundError:
    print(f"Error: File '{filepath}' not found.")
    sys.exit(1)

  # Print results grouped by full sweep (timestamp)
  print(f"{'Date':<12} {'Time':<10} {'Lowest Freq (MHz)':<18} {'Power (dB)':<12}")
  print("-" * 55)

  for (date, time), chunk_mins in sorted(sweeps.items()):
    # Find the absolute lowest bin across all chunks in this sweep timestamp
    absolute_best = min(chunk_mins, key=lambda x: x[1])
    abs_freq_mhz = absolute_best[0] / 1e6
    abs_power = absolute_best[1]

    print(
        f"{date:<12} {time:<10} {abs_freq_mhz:<18.6f} {abs_power:<12.2f}"
    )


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Usage: python parse_rtl_power.py <path_to_log.csv>")
    sys.exit(1)

  csv_file = sys.argv[1]
  parse_rtl_power(csv_file)
