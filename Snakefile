"""Top-level ``snakemake`` file that runs analysis."""

configfile: "config.yaml"

# outputs to build
rule all:
    input:
        "results/ha_subtype_alignment/ha18.newick",
        expand(
            "results/rewritten_pdbs/{pdb}_foldmason_{chain}.pdb",
            pdb=config["pdbs"].keys(),
            chain=["A", "B"],
        ),
        expand(
            "results/foldmason_alignment/chain_{chain}/result_aa.fa",
            chain=["A", "B"],
        ),
        expand(
            "results/dssp/{pdb}_dssp.mmcif",
            pdb=config["pdbs"].keys(),
        ),
        "results/structural_alignment/structural_alignment.csv",
        "results/combined_effects/combined_mutation_effects.csv",
        "results/combined_effects/combined_site_effects.csv",
        "results/divergence/h3_h5_divergence.csv",
        "results/divergence/h3_h7_divergence.csv",
        "results/divergence/h5_h7_divergence.csv",
        "notebooks/calculate_epistatic_shifts.html",
        "notebooks/explain_epistatic_shifts.html",
        "docs/.built",

rule infer_phylogenetic_tree:
    """Infer maximum-likelihood tree of HA subtypes with IQ-TREE."""
    input:
        script="scripts/infer_tree.py",
        alignment=config["ha_subtype_alignment"],
    output:
        tree="results/ha_subtype_alignment/ha18.newick",
    log:
        "logs/infer_tree.log",
    shell:
        """
        python {input.script} {input.alignment} {output.tree} > {log} 2>&1
        """


rule extract_pdb_chain:
    """Extract individual chains from PDB files for Foldmason."""
    input:
        script="scripts/rewrite_pdbs.py",
        pdb="data/pdbs/{pdb}.pdb",
    output:
        "results/rewritten_pdbs/{pdb}_foldmason_{chain}.pdb",
    params:
        model=lambda wildcards: config["pdbs"][wildcards.pdb]["model"],
    shell:
        """
        python {input.script} -i {input.pdb} -o {output} -c {wildcards.chain} -m {params.model}
        """


rule foldmason_alignment:
    """Run Foldmason for multiple structural alignment of HA chains."""
    input:
        script="scripts/foldmason.bash",
        pdbs=expand(
            "results/rewritten_pdbs/{pdb}_foldmason_{{chain}}.pdb",
            pdb=config["pdbs"].keys(),
        ),
    output:
        aa="results/foldmason_alignment/chain_{chain}/result_aa.fa",
    log:
        "logs/foldmason_alignment_chain_{chain}.log",
    shell:
        """
        bash {input.script} {wildcards.chain} results/foldmason_alignment/chain_{wildcards.chain} {input.pdbs} > {log} 2>&1
        """


rule run_dssp:
    """Calculate solvent accessibility with DSSP."""
    input:
        cif=lambda wildcards: config["pdbs"][wildcards.pdb]["cif"],
    output:
        dssp="results/dssp/{pdb}_dssp.mmcif",
    log:
        "logs/dssp_{pdb}.log",
    shell:
        """
        mkdssp {input.cif} {output.dssp} --calculate-accessibility --verbose > {log} 2>&1
        """


rule structural_alignment:
    """Generate structural alignment map of HAs."""
    input:
        notebook="notebooks/structural_alignment.ipynb",
        foldmason_a="results/foldmason_alignment/chain_A/result_aa.fa",
        foldmason_b="results/foldmason_alignment/chain_B/result_aa.fa",
        dssp_files=expand(
            "results/dssp/{pdb}_dssp.mmcif",
            pdb=config["pdbs"].keys(),
        ),
        rmsd_files=config["rmsd_files"],
        cell_entry_files=list(config["cell_entry_files"].values()),
    output:
        csv="results/structural_alignment/structural_alignment.csv",
    log:
        "logs/structural_alignment.log",
    shell:
        """
        jupyter nbconvert --to notebook --execute {input.notebook} \
            --output-dir=notebooks --output=$(basename {input.notebook}) > {log} 2>&1
        """


rule summarize_effects:
    """Summarize mutation effects."""
    input:
        notebook="notebooks/summarize_effects.ipynb",
        structural_aln="results/structural_alignment/structural_alignment.csv",
        cell_entry_files=list(config["cell_entry_files"].values()),
    output:
        mutation_effects="results/combined_effects/combined_mutation_effects.csv",
        site_effects="results/combined_effects/combined_site_effects.csv",
        executed_notebook="results/combined_effects/summarize_effects.ipynb",
    params:
        effect_std_filter=config["filter_params"]["effect_std_filter"],
        times_seen_filter=config["filter_params"]["times_seen_filter"],
        n_selections_filter=config["filter_params"]["n_selections_filter"],
        clip_effect=config["filter_params"]["clip_effect"],
    log:
        "logs/summarize_effects.log",
    shell:
        """
        cd notebooks && papermill summarize_effects.ipynb ../results/combined_effects/summarize_effects.ipynb \
            -p effect_std_filter {params.effect_std_filter} \
            -p times_seen_filter {params.times_seen_filter} \
            -p n_selections_filter {params.n_selections_filter} \
            -p clip_effect {params.clip_effect} > ../{log} 2>&1
        """


rule calculate_epistatic_shifts:
    """Calculate Jensen-Shannon divergence in amino-acid preferences."""
    input:
        notebook="notebooks/calculate_epistatic_shifts.ipynb",
        mutation_effects="results/combined_effects/combined_mutation_effects.csv",
    output:
        h3_h5_divergence="results/divergence/h3_h5_divergence.csv",
        h3_h7_divergence="results/divergence/h3_h7_divergence.csv",
        h5_h7_divergence="results/divergence/h5_h7_divergence.csv",
        html="notebooks/calculate_epistatic_shifts.html",
    log:
        "logs/calculate_epistatic_shifts.log",
    shell:
        """
        jupyter nbconvert --to notebook --execute {input.notebook} \
            --output-dir=notebooks --output=$(basename {input.notebook}) > {log} 2>&1 && \
        jupyter nbconvert --to html {input.notebook} \
            --output-dir=notebooks --output=$(basename {output.html}) >> {log} 2>&1
        """


rule explain_epistatic_shifts:
    """Analyze factors associated with divergence in amino-acid preferences."""
    input:
        notebook="notebooks/explain_epistatic_shifts.ipynb",
        h3_h5_divergence="results/divergence/h3_h5_divergence.csv",
        h3_h7_divergence="results/divergence/h3_h7_divergence.csv",
        h5_h7_divergence="results/divergence/h5_h7_divergence.csv",
        site_effects="results/combined_effects/combined_site_effects.csv",
    output:
        html="notebooks/explain_epistatic_shifts.html",
    log:
        "logs/explain_epistatic_shifts.log",
    shell:
        """
        jupyter nbconvert --to notebook --execute {input.notebook} \
            --output-dir=notebooks --output=$(basename {input.notebook}) > {log} 2>&1 && \
        jupyter nbconvert --to html {input.notebook} \
            --output-dir=notebooks --output=$(basename {output.html}) >> {log} 2>&1
        """

# Include documentation building rules
build_vitepress_homepage = False  # Set to True if you want VitePress integration
other_target_files = []  # For conditional targets

include: "docs.smk"


onsuccess:
    # Clean up PuLP solver temporary files
    shell("rm -f *.mps *.sol")