# Epistatic shifts in hemagglutinin across subtypes
Study by Timothy Yu and Jesse Bloom.

## Conda environment
Build the conda environment using the provided `environment.yml` file in this directory:

```bash
conda env create -f environment.yml 
conda activate ha-epistasis
```

## Downloading DSSP
To download the DSSP annotations, run:
```bash
wget --content-disposition https://pdb-redo.eu/dssp/db/4o5n/legacy
wget --content-disposition https://pdb-redo.eu/dssp/db/4kwm/legacy
wget --content-disposition https://pdb-redo.eu/dssp/db/4r8w/legacy
```

## Running DSSP
To run DSSP to calculate solvent accessibility, run:
```bash
mkdssp structures/pdbs/4O5N-assembly1.cif structures/dssp/4O5N_dssp.mmcif --calculate-accessibility --verbose
mkdssp structures/pdbs/4KWM-assembly1.cif structures/dssp/4KWM_dssp.mmcif --calculate-accessibility --verbose
mkdssp structures/pdbs/4R8W-assembly1-noAb.cif structures/dssp/4R8W_dssp.mmcif --calculate-accessibility --verbose
```