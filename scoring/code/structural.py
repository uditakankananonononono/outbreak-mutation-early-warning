"""Structural-criticality core for the B17 scoring slice.

Computes spike contact sets from published PDB complexes (5 A any-atom cutoff,
spike chains identified by signature motifs) and the SARS-CoV-1 conservation set.
The reference algorithm is validation/code/build_structural.py (byte-locked);
this module re-implements it as an importable library with parameterized input/
output dirs so the reproduce gate (scoring/GATES_LOCKED.md section 3) can prove
byte-identical regeneration of the reference structural_sets.json.
"""
import json, os
from collections import defaultdict

SPIKE_SIGNATURES = ["CPFGEVFNATRFASVY", "NLTTRTQLPPAYTNSF", "GTNTSNQVAVLYQDVN"]

REFERENCE_COMPLEXES = [
    ("6M0J", "ace2_interface", "Lan et al. 2020 Nature doi:10.1038/s41586-020-2180-5"),
    ("6WPT", "epitope_S309",   "Pinto et al. 2020 Nature doi:10.1038/s41586-020-2349-y"),
    ("6XDG", "epitope_REGN",   "Hansen et al. 2020 Science doi:10.1126/science.abd0827"),
    ("7C2L", "epitope_4A8_NTD","Chi et al. 2020 Science doi:10.1126/science.abc6952"),
]

FUNCTIONAL_DOMAINS = {
    "note": "canonical SARS-CoV-2 spike ranges (Wrapp 2020 Science doi:10.1126/science.abb2507; Lan 2020)",
    "NTD": [14, 305], "RBD": [319, 541], "RBM": [437, 508],
    "furin_cleavage_site": [681, 685], "S2_prime": [815, 815],
    "fusion_peptide": [816, 837], "HR1": [920, 970]}

def _chain_seq(chain, ppb):
    return "".join(str(p.get_sequence()) for p in ppb.build_peptides(chain))

def contact_residues(pdb_path, pdb_id, parser, ppb, cutoff=5.0):
    """(contacts {(chain_id, resnum)}, spike_chain_ids, other_chain_ids) for one complex."""
    st = parser.get_structure(pdb_id, pdb_path)
    model = st[0]
    spike_chains, other_chains = [], []
    for ch in model:
        seq = _chain_seq(ch, ppb)
        if any(sig in seq for sig in SPIKE_SIGNATURES):
            spike_chains.append(ch)
        elif seq:
            other_chains.append(ch)
    spike_atoms = [(ch.id, at) for ch in spike_chains for res in ch for at in res
                   if res.id[0] == " "]
    other_atoms = [at for ch in other_chains for res in ch for at in res if res.id[0] == " "]
    grid = defaultdict(list); gs = cutoff + 2.0
    for at in other_atoms:
        grid[tuple(int(c / gs) for c in at.coord)].append(at)
    contacts = set()
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

def conserved_vs_sars1(sars2_fasta, sars1_fasta):
    """1-based SARS-CoV-2 spike positions identical to SARS-CoV-1 spike (global alignment)."""
    from Bio.Align import PairwiseAligner
    s2 = "".join(l.strip() for l in open(sars2_fasta) if not l.startswith(">"))
    s1 = "".join(l.strip() for l in open(sars1_fasta) if not l.startswith(">"))
    al = PairwiseAligner(); al.mode = "global"; al.open_gap_score = -10; al.extend_gap_score = -0.5
    a = al.align(s2, s1)[0]
    blocks2, blocks1 = a.aligned
    conserved = []
    for (s2a, s2b), (s1a, s1b) in zip(blocks2, blocks1):
        for i in range(s2b - s2a):
            if s2[s2a + i] == s1[s1a + i]:
                conserved.append(int(s2a + i + 1))
    return conserved

def build_reference_sets(raw_dir):
    """Build the reference structural_sets dict from byte-locked inputs in raw_dir.
    Dict construction order and content mirror validation/code/build_structural.py
    exactly so the serialized JSON is byte-identical."""
    from Bio.PDB import PDBParser, PPBuilder
    parser = PDBParser(QUIET=True); ppb = PPBuilder()
    out = {"method": "spike residues with any atom <=5A of a different chain; "
                     "spike chains identified by motif match", "sources": {}}
    stats = []
    for pdb_id, label, cite in REFERENCE_COMPLEXES:
        contacts, sch, och = contact_residues(os.path.join(raw_dir, pdb_id + ".pdb"),
                                              pdb_id, parser, ppb)
        res = sorted({n for (_c, n) in contacts if 1 <= n <= 1273})
        out["sources"][label] = {"pdb": pdb_id, "citation": cite,
                                 "spike_chains": sch, "partner_chains": och,
                                 "residues": res}
        stats.append((pdb_id, label, len(res), sch, och))
    epi = sorted(set(out["sources"]["epitope_S309"]["residues"]) |
                 set(out["sources"]["epitope_REGN"]["residues"]) |
                 set(out["sources"]["epitope_4A8_NTD"]["residues"]))
    out["epitope_surface_union"] = epi
    out["conserved_sars1"] = {
        "method": "biopython global alignment YP_009724390.1 vs NP_828851.1, identical residues",
        "residues": conserved_vs_sars1(os.path.join(raw_dir, "sars2_spike.fasta"),
                                       os.path.join(raw_dir, "sars1_spike.fasta"))}
    out["functional_domains"] = FUNCTIONAL_DOMAINS
    return out, stats

def load_score_sets(sets):
    """Flatten a structural_sets dict into the five scored sets + locked weights."""
    dom = sets["functional_domains"]
    return {
        "epitope": set(sets["epitope_surface_union"]),
        "ace2": set(sets["sources"]["ace2_interface"]["residues"]),
        "cleavage": set(range(dom["furin_cleavage_site"][0], dom["furin_cleavage_site"][1]+1)) |
                    set(range(dom["S2_prime"][0], dom["S2_prime"][1]+1)),
        "domain": (set(range(dom["RBM"][0], dom["RBM"][1]+1)) |
                   set(range(dom["fusion_peptide"][0], dom["fusion_peptide"][1]+1)) |
                   set(range(dom["HR1"][0], dom["HR1"][1]+1))),
        "conserved": set(sets["conserved_sars1"]["residues"]),
    }

W = {"epitope": 0.35, "ace2": 0.25, "cleavage": 0.15, "domain": 0.15, "conserved": 0.10}

def parse_mutation(mut):
    """'S:N501Y' -> (gene, ref_aa, pos, alt_aa). Raises ValueError on malformed input."""
    if not isinstance(mut, str) or ":" not in mut:
        raise ValueError("expected 'GENE:RefPosAlt', got %r" % (mut,))
    gene, rest = mut.split(":", 1)
    if (not gene or len(rest) < 3 or not rest[0].isalpha() or not rest[-1].isalpha()
            or not rest[1:-1].isdigit()):
        raise ValueError("expected 'GENE:RefPosAlt', got %r" % (mut,))
    return gene, rest[0], int(rest[1:-1]), rest[-1]

def structural_score(mut, S):
    """Base criticality weight S in [0,1]. Locked formula = reference engine.
    Spike-only weighting (non-spike -> 0.0, documented limitation)."""
    gene, _ref, pos, _alt = parse_mutation(mut)
    if gene != "S":
        return 0.0
    return (W["epitope"] * (pos in S["epitope"]) + W["ace2"] * (pos in S["ace2"]) +
            W["cleavage"] * (pos in S["cleavage"]) + W["domain"] * (pos in S["domain"]) +
            W["conserved"] * (pos in S["conserved"]))

def score_breakdown(mut, S):
    """Per-component breakdown + confidence tier (tiers never change S)."""
    gene, _ref, pos, _alt = parse_mutation(mut)
    if gene != "S":
        return {"S": 0.0, "tier": "UNRESOLVED",
                "reason": "non-spike gene; structural weighting covers spike only",
                "components": {}}
    comp = {k: (pos in S[k]) for k in ("epitope", "ace2", "cleavage", "domain", "conserved")}
    s = structural_score(mut, S)
    if comp["epitope"] or comp["ace2"]:
        tier = "TIER-1 STRUCTURE-DIRECT"
    elif comp["cleavage"] or comp["domain"]:
        tier = "TIER-2 DOMAIN-INFERRED"
    elif comp["conserved"]:
        tier = "TIER-3 CONSERVATION-ONLY"
    elif 1 <= pos <= 1273:
        tier = "THIN"
    else:
        tier = "UNRESOLVED"
    out = {"S": s, "tier": tier, "components": {k: (W[k] if v else 0.0) for k, v in comp.items()}}
    if tier == "THIN":
        out["reason"] = "canonical spike residue, no structural signal"
    elif tier == "UNRESOLVED":
        out["reason"] = "residue outside canonical spike range 1-1273"
    return out
