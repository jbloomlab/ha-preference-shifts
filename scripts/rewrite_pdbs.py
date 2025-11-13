#!/usr/bin/env python
"""
Extract specific chains from PDB files.

This script can be used to extract one or more chains from a PDB structure file.
Useful for preparing structures for tools like Foldmason.
"""

import argparse
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select


def extract_chain(input_pdb, output_pdb, chain_ids, model_id=0):
    """
    Extract specific chains from a PDB file.

    Parameters
    ----------
    input_pdb : str or Path
        Path to input PDB file
    output_pdb : str or Path
        Path to output PDB file
    chain_ids : list of str
        List of chain IDs to extract (e.g., ['A', 'B'])
    model_id : int, default=0
        Model ID to extract (0-indexed)
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", str(input_pdb))

    class ChainSelect(Select):
        def accept_model(self, model):
            return model.get_id() == model_id

        def accept_chain(self, chain):
            return chain.get_id() in chain_ids

    io = PDBIO()
    io.set_structure(structure)
    io.save(str(output_pdb), ChainSelect())


def main():
    parser = argparse.ArgumentParser(
        description="Extract specific chains from PDB files"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input PDB file"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output PDB file"
    )
    parser.add_argument(
        "-c", "--chains",
        required=True,
        nargs="+",
        help="Chain IDs to extract (e.g., A B)"
    )
    parser.add_argument(
        "-m", "--model",
        type=int,
        default=0,
        help="Model ID to extract (default: 0)"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Extract chains
    extract_chain(
        input_pdb=args.input,
        output_pdb=args.output,
        chain_ids=args.chains,
        model_id=args.model
    )

    print(f"Extracted chains {args.chains} from {args.input} to {args.output}")


if __name__ == "__main__":
    main()
