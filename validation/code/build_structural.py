#!/usr/bin/env python3
"""Build static structural-criticality residue sets from published PDB complexes.
Method: for each complex, identify spike-derived chains by signature motifs,
then collect spike residues with any atom within 5 Angstrom of a different chain.
Outputs data/static/structural_sets.json (byte-locked by the slice manifest)."""
import json, os
from Bio.PDB import PDBParser, PPBuilder
from Bio.Align import PairwiseAligner

HERE = os.path.dirname(__file__); RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "static"); os.makedirs(OUT, exist_ok=True)

SPIKE_SIGNATURES = ["CPFGEVFNATRFASVY", "NLTTRTQLPPAYTNSF", "GTNTSNQVAVLYQDVN"]
parser = PDBParser(QUIET=True); ppb = PPBuilder()

def chain_seq(chain):
    seq = "".join(str(p.get_sequence()) for p in ppb.build_peptides(chain))
    return seq

def contact_residues(pdb_id, cutoff=5.0):
    """Return (spike residue numbers in contact with other chains, chain map)."""
    st = parser.get_structure(pdb_id, os.path.join(RAW, pdb_id + ".pdb"))
    model = st[0]
    spike_chains, other_chains = [], []
    for ch in model:
        seq = chain_seq(ch)
        if any(sig in seq for sig in SPIKE_SIGNATURES): spike_chains.append(ch)
        elif seq: other_chains.append(ch)
    contacts = set()
    spike_atoms = [(ch.id, at) for ch in spike_chains for res in ch for at in res
                   if res.id[0] == " "]
    other_atoms = [at for ch in other_chains for res in ch for at in res if res.id[0] == " "]
    # coarse grid to keep it fast enough
    from collections import defaultdict
    grid = defaultdict(list); gs = cutoff + 2.0
    for at in other_atoms:
        k = tuple(int(c / gs) for c in at.coord)
        grid[k].append(at)
    for ch_id, at in spike_atoms:
        k = tuple(int(c / gs) for c in at.coord)
        hit = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for oa in grid.get((k[0]+dx, k[1]+dy, k[2]+dz), []):
                        if (at.coord - oa.coord) @ (at.coord - oa.coord) <= cutoff**2:
                            hit = True; break
                    if hit: break
                if hit: break
            if hit: break
        if hit:
            contacts.add((ch_id, at.get_parent().id[1]))
    return contacts, [c.id for c in spike_chains], [c.id for c in other_chains]

def main():
    out = {"method": "spike residues with any atom <=5A of a different chain; "
                     "spike chains identified by motif match", "sources": {}}
    for pdb_id, label, cite in [
        ("6M0J", "ace2_interface", "Lan et al. 2020 Nature doi:10.1038/s41586-020-2180-5"),
        ("6WPT", "epitope_S309",   "Pinto et al. 2020 Nature doi:10.1038/s41586-020-2349-y"),
        ("6XDG", "epitope_REGN",   "Hansen et al. 2020 Science doi:10.1126/science.abd0827"),
        ("7C2L", "epitope_4A8_NTD","Chi et al. 2020 Science doi:10.1126/science.abc6952"),
    ]:
        contacts, sch, och = contact_residues(pdb_id)
        # residue numbering is consistent across chains of the same construct;
        # keep residues in canonical spike range 1-1273
        res = sorted({n for (_c, n) in contacts if 1 <= n <= 1273})
        out["sources"][label] = {"pdb": pdb_id, "citation": cite,
                                 "spike_chains": sch, "partner_chains": och,
                                 "residues": res}
        print(pdb_id, label, len(res), "contact residues; spike chains", sch, "partners", och)
    epi = sorted(set(out["sources"]["epitope_S309"]["residues"]) |
                 set(out["sources"]["epitope_REGN"]["residues"]) |
                 set(out["sources"]["epitope_4A8_NTD"]["residues"]))
    out["epitope_surface_union"] = epi
    print("epitope union:", len(epi))

    # conservation vs SARS-CoV-1 spike (global alignment, identical positions)
    s1 = "".join(l.strip() for l in open(os.path.join(RAW, "sars1_spike.fasta")) if not l.startswith(">"))
    s2 = "".join(l.strip() for l in open(os.path.join(RAW, "sars2_spike.fasta")) if not l.startswith(">"))
    al = PairwiseAligner(); al.mode = "global"; al.open_gap_score = -10; al.extend_gap_score = -0.5
    a = al.align(s2, s1)[0]
    blocks2, blocks1 = a.aligned
    conserved = []
    for (s2a, s2b), (s1a, s1b) in zip(blocks2, blocks1):
        for i in range(s2b - s2a):
            if s2[s2a + i] == s1[s1a + i]: conserved.append(int(s2a + i + 1))  # 1-based
    out["conserved_sars1"] = {"method": "biopython global alignment YP_009724390.1 vs NP_828851.1, identical residues",
                              "residues": conserved}
    print("conserved:", len(conserved), "of", len(s2))
    out["functional_domains"] = {
        "note": "canonical SARS-CoV-2 spike ranges (Wrapp 2020 Science doi:10.1126/science.abb2507; Lan 2020)",
        "NTD": [14, 305], "RBD": [319, 541], "RBM": [437, 508],
        "furin_cleavage_site": [681, 685], "S2_prime": [815, 815],
        "fusion_peptide": [816, 837], "HR1": [920, 970]}
    json.dump(out, open(os.path.join(OUT, "structural_sets.json"), "w"), indent=1)
    print("wrote structural_sets.json")

main()
