#!/usr/bin/env python
"""
Build a maximum-likelihood phylogenetic tree using IQ-TREE.
"""

import subprocess
import os
import sys
from pathlib import Path
from Bio import AlignIO, Phylo

def main():
    # Parse command-line arguments
    if len(sys.argv) < 3:
        print("Usage: python infer_tree.py <alignment_file> <output_tree_file>")
        print("Example: python infer_tree.py data/alignment.fasta results/tree.newick")
        sys.exit(1)

    alignment_file = sys.argv[1]
    output_tree_file = sys.argv[2]

    # Derive output directory and prefix from the output tree file
    output_path = Path(output_tree_file)
    output_dir = output_path.parent
    output_prefix = output_dir / output_path.stem

    # Read alignment for reference
    aln = AlignIO.read(alignment_file, "fasta")
    print(f"Loaded alignment with {len(aln)} sequences")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Run IQ-TREE with maximum-likelihood inference
    # -m TEST: automatically select best-fit amino acid substitution model
    # -bb 1000: ultrafast bootstrap with 1000 replicates (optional, can adjust or remove)
    # -nt AUTO: automatically determine number of threads
    iqtree_cmd = [
        "iqtree",
        "-s", alignment_file,
        "-m", "TEST",  # Automatic model selection (not specific model like "LG", "WAG", "JTT")
        "-bb", "1000",  # Ultrafast bootstrap
        "-nt", "AUTO",
        "-pre", str(output_prefix),  # Prefix for output files
        "-redo"  # Overwrite existing results
    ]

    print("Running IQ-TREE maximum-likelihood inference...")
    print(f"Command: {' '.join(iqtree_cmd)}")
    result = subprocess.run(iqtree_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"IQ-TREE failed with return code {result.returncode}")

    print("IQ-TREE completed successfully!")

    # Show some output
    print("\n--- IQ-TREE Output (last 50 lines) ---")
    stdout_lines = result.stdout.split('\n')
    for line in stdout_lines[-50:]:
        print(line)

    print("\n--- Best model selected ---")
    # Parse the log file to show the best model
    log_file = f"{output_prefix}.log"
    with open(log_file) as f:
        for line in f:
            if "Best-fit model:" in line:
                print(line.strip())
                break

    # Read the resulting tree
    treefile = f"{output_prefix}.treefile"
    tree = Phylo.read(treefile, "newick")

    # Remove names from internal nodes (keep support values if present)
    for clade in tree.get_nonterminals():
        if clade.confidence is None:
            clade.name = None

    # Copy the tree to a standard .newick file for compatibility
    Phylo.write(tree, output_tree_file, "newick")
    print(f"\nTree saved to {output_tree_file}")

    print("\n--- Tree ASCII visualization ---")
    Phylo.draw_ascii(tree)

if __name__ == "__main__":
    main()
