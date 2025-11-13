#!/bin/bash
set -euo pipefail

# Run Foldmason structural alignment for HA chains
# Usage: foldmason.bash <chain> <output_dir> <pdb1> <pdb2> [pdb3 ...]

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <chain> <output_dir> <pdb1> <pdb2> [pdb3 ...]"
    echo "Example: $0 A results/foldmason_alignment results/rewritten_pdbs/4o5n_foldmason_A.pdb results/rewritten_pdbs/4kwm_foldmason_A.pdb"
    exit 1
fi

CHAIN="$1"
OUTPUT_DIR="$2"
shift 2
INPUT_PDBS=("$@")

# Convert paths to absolute paths
OUTPUT_DIR=$(realpath "$OUTPUT_DIR")
ABS_INPUT_PDBS=()
for pdb in "${INPUT_PDBS[@]}"; do
    ABS_INPUT_PDBS+=("$(realpath "$pdb")")
done

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create a temporary directory for foldmason working files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Run Foldmason alignment
cd "$TEMP_DIR"
foldmason easy-msa "${ABS_INPUT_PDBS[@]}" result foldmason_tmp --report-mode 1

# Move results to output directory
mv result_aa.fa "${OUTPUT_DIR}/result_aa.fa"
mv result.html "${OUTPUT_DIR}/result.html"
mv result.nw "${OUTPUT_DIR}/result.nw"

# Extract pairwise alignments for all combinations
# Get base names without path and extension
declare -a PDB_IDS
for pdb_path in "${INPUT_PDBS[@]}"; do
    # Extract just the PDB ID (e.g., "4o5n" from "results/rewritten_pdbs/4o5n_foldmason_A.pdb")
    pdb_id=$(basename "$pdb_path" | sed 's/_foldmason_.*$//')
    PDB_IDS+=("$pdb_id")
done

# Generate specific pairwise alignments
# H3-H5 comparison (4o5n vs 4kwm)
awk -v a=">4o5n_foldmason_${CHAIN}" -v b=">4kwm_foldmason_${CHAIN}" \
    '/^>/ {p=($0==a || $0==b)} p' \
    "${OUTPUT_DIR}/result_aa.fa" > "${OUTPUT_DIR}/4o5n_4kwm_chain${CHAIN}_aln.fasta"

# H3-H7 comparison (4o5n vs 6ii9)
awk -v a=">4o5n_foldmason_${CHAIN}" -v b=">6ii9_foldmason_${CHAIN}" \
    '/^>/ {p=($0==a || $0==b)} p' \
    "${OUTPUT_DIR}/result_aa.fa" > "${OUTPUT_DIR}/4o5n_6ii9_chain${CHAIN}_aln.fasta"

# H7-H5 comparison (6ii9 vs 4kwm)
awk -v a=">6ii9_foldmason_${CHAIN}" -v b=">4kwm_foldmason_${CHAIN}" \
    '/^>/ {p=($0==a || $0==b)} p' \
    "${OUTPUT_DIR}/result_aa.fa" > "${OUTPUT_DIR}/6ii9_4kwm_chain${CHAIN}_aln.fasta"

echo "Foldmason alignment complete for chain ${CHAIN}. Results in ${OUTPUT_DIR}"