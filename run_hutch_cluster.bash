#!/bin/bash
#SBATCH -c 8

snakemake -j 8 -s Snakefile --rerun-incomplete