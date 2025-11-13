# Comparing mutation effects to influenza HA subtypes
Study by Timothy Yu and Jesse Bloom.

## Conda environment
Build the conda environment using the provided `environment.yml` file in this directory:

```bash
conda env create -f environment.yml 
```

## Snakemake pipeline
Some of the analyses are automated by [snakemake](https://snakemake.readthedocs.io/en/stable/). To run the pipeline:
```bash
conda activate ha-epistasis
snakemake -j 8 -s Snakefile --rerun-incomplete
```

To run on the Hutch cluster via [slurm](https://slurm.schedmd.com/), you can run:
```bash
sbatch -c 8 run_hutch_cluster.bash
```

Note that some parts of the analysis depend on a local installation of ChimeraX. The files in [data/rmsd](data/rmsd) were pre-generated so that the pipeline runs in a single go, but they depend on files generated in the pipeline. To reproduce them, open the ChimeraX scripts [rmsd_ha1.cxc](scripts/non_pipeline_scripts/rmsd_ha1.cxc) and [rmsd_ha2.cxc](scripts/non_pipeline_scripts/rmsd_ha2.cxc) in ChimeraX.

