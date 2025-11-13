#!/usr/bin/env python3
"""
Calculate the RMSD (Root Mean Square Deviation) of RMSD values from files.

This script reads RMSD files from the results/rmsd directory and calculates
the RMSD of the RMSD values in each file (excluding None values).
"""

import numpy as np
from pathlib import Path


def read_rmsd_file(filepath):
    """
    Read RMSD values from a file.

    Parameters
    ----------
    filepath : str or Path
        Path to the RMSD file

    Returns
    -------
    header : str
        The header line from the file
    values : list of float
        List of RMSD values (excluding None values)
    """
    values = []
    header = None

    with open(filepath, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            if i == 0:
                # First line is the header
                header = line
                continue

            # Parse line format: "position: value"
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    value_str = parts[1].strip()
                    if value_str != 'None':
                        try:
                            values.append(float(value_str))
                        except ValueError:
                            pass  # Skip invalid values

    return header, values


def calculate_rmsd(values):
    """
    Calculate RMSD of a list of values.

    RMSD = sqrt(mean(values^2))

    Parameters
    ----------
    values : list of float
        List of values

    Returns
    -------
    float
        The RMSD of the values
    """
    if not values:
        return 0.0

    values_array = np.array(values)
    return np.sqrt(np.mean(values_array ** 2))


def main():
    """Main function to process all RMSD files."""
    # Get the script directory and construct path to rmsd directory
    script_dir = Path(__file__).parent
    rmsd_dir = script_dir.parent.parent / 'data' / 'rmsd'

    # Find all .txt files in the rmsd directory
    rmsd_files = sorted(rmsd_dir.glob('*.txt'))

    if not rmsd_files:
        print(f"No RMSD files found in {rmsd_dir}")
        return

    print("RMSD of RMSD values for each file:")
    print("=" * 80)

    results = []

    for filepath in rmsd_files:
        header, values = read_rmsd_file(filepath)

        if values:
            rmsd = calculate_rmsd(values)
            n_values = len(values)

            # Determine domain from filename
            domain = 'ha1' if 'ha1' in filepath.name.lower() else 'ha2'

            results.append({
                'filename': filepath.name,
                'header': header,
                'rmsd': rmsd,
                'n_values': n_values,
                'domain': domain
            })

    # Print results
    for result in results:
        print(f"\nFile: {result['filename']}")
        print(f"Description: {result['header']}")
        print(f"Number of values: {result['n_values']}")
        print(f"RMSD: {result['rmsd']:.4f}")

    print("\n" + "=" * 80)
    print("\nSummary:")
    print(f"Total files processed: {len(results)}")

    # Print comparison table
    print("\nComparison Table:")
    print(f"{'File':<30} {'N':<8} {'RMSD':<10}")
    print("-" * 50)
    for result in results:
        print(f"{result['filename']:<30} {result['n_values']:<8} {result['rmsd']:<10.4f}")

    # Calculate domain-specific averages
    print("\n" + "=" * 80)
    print("\nDomain-Specific RMSD Averages:")
    print("-" * 50)

    # Group by domain
    ha1_rmsds = [r['rmsd'] for r in results if r['domain'] == 'ha1']
    ha2_rmsds = [r['rmsd'] for r in results if r['domain'] == 'ha2']

    if ha1_rmsds:
        ha1_mean = np.mean(ha1_rmsds)
        ha1_std = np.std(ha1_rmsds)
        print(f"\nHA1 domain:")
        print(f"  Number of comparisons: {len(ha1_rmsds)}")
        print(f"  Mean RMSD: {ha1_mean:.4f} Å")
        print(f"  Std Dev: {ha1_std:.4f} Å")
        print(f"  Range: {min(ha1_rmsds):.4f} - {max(ha1_rmsds):.4f} Å")

    if ha2_rmsds:
        ha2_mean = np.mean(ha2_rmsds)
        ha2_std = np.std(ha2_rmsds)
        print(f"\nHA2 domain:")
        print(f"  Number of comparisons: {len(ha2_rmsds)}")
        print(f"  Mean RMSD: {ha2_mean:.4f} Å")
        print(f"  Std Dev: {ha2_std:.4f} Å")
        print(f"  Range: {min(ha2_rmsds):.4f} - {max(ha2_rmsds):.4f} Å")

    # Overall comparison
    if ha1_rmsds and ha2_rmsds:
        print(f"\nComparison:")
        print(f"  HA1 is {'more' if ha1_mean > ha2_mean else 'less'} variable than HA2")
        print(f"  Difference: {abs(ha1_mean - ha2_mean):.4f} Å ({abs(ha1_mean - ha2_mean) / ha2_mean * 100:.1f}%)")


if __name__ == "__main__":
    main()
