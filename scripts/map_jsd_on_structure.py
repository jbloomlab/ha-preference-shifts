"""writes .defattr for quantitively visualizing JSD each site on HA structure."""

import pandas as pd
from Bio.PDB import PDBParser

def parse_chain_sites(pdb_path):
    """
    Parses a PDB file to extract site numbers for each chain.
    Adjusts site numbers for chains B, D, and F by adding 329.
    This function assumes the PDB:
        - Contains chains A-F, where A,C,E are HA1 and B,D,F are HA2.
        - Follows H3 numbering convention.

    Parameters:
        pdb_path (str): Path to the PDB file.
    
    Returns:
        dict: A dictionary with chain IDs as keys and a list of site numbers as values.
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_path)
    chain_sites = {}

    for model in structure:
        for chain in model:
            chain_id = chain.id
            # Extract residue site numbers
            sites = [residue.id[1] for residue in chain if residue.id[0] == " "]
            # Adjust sites for specific chains
            if chain_id in {"B", "D", "F"}:
                sites = [site + 329 for site in sites]
            chain_sites[chain_id] = sites

    return chain_sites

def write_defattr(infile, outfile, name, chain_mapping):
    df = pd.read_csv(infile).dropna()

    # Write the output file
    with open(outfile, 'w') as f:
        # Write header lines
        f.write(f'attribute: {name}\n')
        f.write('match mode: 1-to-1\n')
        f.write('recipient: residues\n')
    
        # Write the formatted data for each chain
        for chain_id, chain_sites in chain_mapping.items():
            for site in chain_sites:
                residue = site if site < 330 else (site - 329)
                effect_value = df.loc[
                    df['struct_site'] == str(site), name
                ].values
                if len(effect_value) > 0:
                    effect_value = effect_value[0]
                    f.write(f'\t/{chain_id}:{residue}\t{effect_value:.6f}\n')

# Define the chain mappings

#4O5N
chain_mapping_4o5n = parse_chain_sites('../structures/pdbs/4o5n.pdb')

# Takes input .csv and exports .defattr.
write_defattr(
    '../results/jensen_shannon_divergence/jsd_h3_h5.csv',
    '../results/jensen_shannon_divergence/jsd_h3_h5.defattr',
    'JS_h3_vs_h5',
    chain_mapping_4o5n,
)

write_defattr(
    '../results/jensen_shannon_divergence/jsd_h3_h7.csv',
    '../results/jensen_shannon_divergence/jsd_h3_h7.defattr',
    'JS_h3_vs_h7',
    chain_mapping_4o5n,
)

write_defattr(
    '../results/jensen_shannon_divergence/jsd_h5_h7.csv',
    '../results/jensen_shannon_divergence/jsd_h5_h7.defattr',
    'JS_h5_vs_h7',
    chain_mapping_4o5n,
)