#!/usr/bin/env python3
"""
Replace H3, H5, H7 sequences in ha18_alignment.fasta with structurally-aligned versions.

This script identifies the existing H3N2, H5N1, and H7N9 sequences in ha18_alignment.fasta
and replaces them with the structurally-aligned versions from structural_alignment.csv,
while keeping all other sequences unchanged.

Input:
  - data/ha18_alignment.fasta
  - results/structural_alignment/structural_alignment.csv

Output:
  - data/ha18_alignment_revised.fasta
"""

import pandas as pd
from Bio import SeqIO, AlignIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import subprocess
from pathlib import Path
import tempfile

# Read structural alignment and extract H3, H5, H7 sequences with gaps preserved
struct_df = pd.read_csv('../../results/structural_alignment/structural_alignment.csv')

# Define proper sequence names
sequence_names = {
    'h3_wt_aa': 'A/Massachusetts/18/2022/H3N2',
    'h5_wt_aa': 'A/American_Wigeon/South_Carolina/USDA-000345-001/2021/H5N1',
    'h7_wt_aa': 'A/Anhui/1/2013/H7N9'
}

# Map to H subtypes for matching
subtype_map = {
    'h3_wt_aa': 'H3N2',
    'h5_wt_aa': 'H5N1',
    'h7_wt_aa': 'H7N9'
}

structural_seqs = {}
for col, name in sequence_names.items():
    structural_seqs[subtype_map[col]] = {
        'name': name,
        'seq': ''.join(row[col] if pd.notna(row[col]) else '-'
                       for _, row in struct_df.iterrows())
    }

print(f"Created structural sequences: {len(structural_seqs[list(subtype_map.values())[0]]['seq'])} positions")

# Read the 18-sequence MSA
msa_18 = AlignIO.read('../../data/ha18_alignment.fasta', 'fasta')

# Identify which sequences to replace and which to keep
sequences_to_align = []  # Non-H3/H5/H7 sequences (ungapped)
replaced_subtypes = []

for record in msa_18:
    # Extract subtype from sequence ID (e.g., H3N2, H5N1, H7N7, etc.)
    full_subtype = record.id.split('/')[-1]
    # Extract just the H# part for matching
    h_subtype = full_subtype.split('N')[0]  # e.g., H3, H5, H7

    # Check if we should replace this sequence
    matched_subtype = None
    for subtype, info in structural_seqs.items():
        if subtype.startswith(h_subtype):
            matched_subtype = subtype
            break

    if matched_subtype:
        print(f"Will replace: {record.id} -> {structural_seqs[matched_subtype]['name']}")
        replaced_subtypes.append(matched_subtype)
    else:
        # Keep this sequence - ungap it for realignment
        ungapped_seq = str(record.seq).replace('-', '')
        sequences_to_align.append(SeqRecord(Seq(ungapped_seq), id=record.id, description=''))

print(f"\nKeeping {len(sequences_to_align)} sequences")
print(f"Replacing {len(replaced_subtypes)} sequences with structural versions")

# Create seed alignment with the 3 structural sequences
with tempfile.TemporaryDirectory() as tmpdir:
    ungapped_path = Path(tmpdir) / 'other_seqs.fasta'
    struct_path = Path(tmpdir) / 'structural_seed.fasta'

    # Write non-H3/H5/H7 sequences
    SeqIO.write(sequences_to_align, ungapped_path, 'fasta')

    # Write structural seed alignment
    with open(struct_path, 'w') as f:
        for subtype in ['H3N2', 'H5N1', 'H7N9']:
            if subtype in structural_seqs:
                f.write(f">{structural_seqs[subtype]['name']}\n")
                f.write(f"{structural_seqs[subtype]['seq']}\n")

    print("\nRunning MAFFT with structural seed...")

    # Run MAFFT with --seed to preserve structural alignment
    cmd = [
        'mafft',
        '--seed', str(struct_path),
        '--auto',
        str(ungapped_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Remove "_seed_" prefix that MAFFT adds to seed sequences
        cleaned_output = result.stdout.replace('>_seed_', '>')

        # Write output
        output_path = Path('../../data/ha18_alignment_revised.fasta')
        with open(output_path, 'w') as f:
            f.write(cleaned_output)

        # Verify
        alignment = AlignIO.read(output_path, 'fasta')
        print(f"✓ Created {output_path}")
        print(f"  Sequences: {len(alignment)}")
        print(f"  Alignment length: {alignment.get_alignment_length()}")

    except subprocess.CalledProcessError as e:
        print(f"Error running MAFFT: {e}")
        print(f"stderr: {e.stderr}")
