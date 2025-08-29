#!/bin/bash

foldmason easy-msa \
  ../structures/rewritten_pdbs/4o5n_foldmason_A.pdb \
  ../structures/rewritten_pdbs/4kwm_foldmason_A.pdb \
  ../structures/rewritten_pdbs/4r8w_foldmason_A.pdb \
  result ../foldmason --report-mode 1

mkdir ../results/foldmason/ha1
mv result_aa.fa ../results/foldmason/ha1/result_aa.fa
mv result_3di.fa ../results/foldmason/ha1/result_3di.fa
mv result.html ../results/foldmason/ha1/result.html
mv result.nw ../results/foldmason/ha1/result.nw

pairs=("4o5n 4r8w" "4o5n 4kwm" "4r8w 4kwm")
for pair in "${pairs[@]}"; do
  set -- $pair
  id1="$1"; id2="$2"
  awk -v a=">${id1}_foldmason_A" -v b=">${id2}_foldmason_A" \
      '/^>/ {p=($0==a || $0==b)} p' \
      ../results/foldmason/ha1/result_aa.fa > "../results/foldmason/ha1/${id1}_${id2}_ha1_aln.fasta"
done

foldmason easy-msa \
  ../structures/rewritten_pdbs/4o5n_foldmason_B.pdb \
  ../structures/rewritten_pdbs/4kwm_foldmason_B.pdb \
  ../structures/rewritten_pdbs/4r8w_foldmason_B.pdb \
  result ../foldmason --report-mode 1

mkdir ../results/foldmason/ha2
mv result_aa.fa ../results/foldmason/ha2/result_aa.fa
mv result_3di.fa ../results/foldmason/ha2/result_3di.fa
mv result.html ../results/foldmason/ha2/result.html
mv result.nw ../results/foldmason/ha2/result.nw

pairs=("4o5n 4r8w" "4o5n 4kwm" "4r8w 4kwm")
for pair in "${pairs[@]}"; do
  set -- $pair
  id1="$1"; id2="$2"
  awk -v a=">${id1}_foldmason_B" -v b=">${id2}_foldmason_B" \
      '/^>/ {p=($0==a || $0==b)} p' \
      ../results/foldmason/ha2/result_aa.fa > "../results/foldmason/ha2/${id1}_${id2}_ha2_aln.fasta"
done