#!/usr/bin/env python3
"""Build a Type-valued Eq analogue followed by the canonical Quot suffix."""
import argparse
import json
from pathlib import Path

REF_KEYS = {
    "ie": "e", "type": "e", "body": "e", "fn": "e", "arg": "e",
    "rhs": "e", "value": "e",
    "name": "n", "pre": "n", "in": "n", "param": "n",
    "levelParams": "n", "all": "n", "ctors": "n", "induct": "n",
    "ctor": "n",
    "il": "l", "sort": "l", "us": "l", "succ": "l", "max": "l",
    "imax": "l",
}

def rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]

def ids(row):
    out=[]
    for k,v in row.items():
        if k in ("ie","in","il"):
            out.append((k,v))
    return out

def rewrite(v, maps, local, key=None):
    if isinstance(v, dict):
        return {k: rewrite(x, maps, local, k) for k,x in v.items()}
    if isinstance(v, list):
        return [rewrite(x, maps, local, key) for x in v]
    if isinstance(v, int) and key in REF_KEYS:
        domain=REF_KEYS[key]
        return maps[domain].get(v, local[domain].get(v, v))
    return v

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("alternate", type=Path)
    ap.add_argument("canonical", type=Path)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("control", type=Path)
    args=ap.parse_args()
    alt, canon=rows(args.alternate), rows(args.canonical)
    if len(alt) not in {60, 62} or len(canon) < 61:
        raise SystemExit("unexpected template sizes")
    # Semantic anchors from canonical Eq to the generated Type-valued analogue.
    # Positional record mapping is invalid because the alternate graph contains
    # an extra successor level and omits the canonical Prop relation helpers.
    maps = {
        "n": {1: 1, 2: 2, 3: 3, 4: 4, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14},
        "l": {0: 0, 1: 1, 2: 4},
        "e": {1: 1, 2: 2, 7: 7, 13: 13, 17: 17, 25: 25, 26: 26, 30: 30},
    }
    # Quot still needs the canonical Prop-valued relation A -> A -> Prop.
    # Import expressions 3, 4, and 5 under fresh IDs after the alternate graph.
    first_helper = max(
        value for row in alt for key, value in ids(row) if key == "ie"
    ) + 1
    helper_ids = {3: first_helper, 4: first_helper + 1, 5: first_helper + 2}
    maps["e"].update(helper_ids)
    used={d:set(m.values()) for d,m in maps.items()}
    next_id={d:(max(s)+1 if s else 0) for d,s in used.items()}
    local={d:{} for d in maps}
    helpers = []
    helper_local = {"e": helper_ids, "n": {}, "l": {}}
    for row in canon[13:16]:
        helpers.append(rewrite(row, maps, helper_local))

    suffix=[]
    for row in canon[60:]:
        # Allocate IDs declared by this suffix record before rewriting edges.
        for k,v in ids(row):
            d=REF_KEYS[k]
            if v not in local[d]:
                local[d][v] = next_id[d]
                next_id[d] += 1
        suffix.append(rewrite(row,maps,local))
    output=[rewrite(r,{"e":{},"n":{},"l":{}},{"e":{},"n":{},"l":{}}) for r in alt]
    for r in output:
        if "str" in r and r["str"].get("str") == "LALAltEq": r["str"]["str"]="Eq"
        if "str" in r and r["str"].get("str") == "LALAltEq.refl": r["str"]["str"]="Eq.refl"
        if "str" in r and r["str"].get("str") == "LALAltEq.rec": r["str"]["str"]="Eq.rec"
        # The generated template chose the opposite fresh-name ordering from
        # the canonical export. Quot checking reconstructs its universe by
        # the literal name `u`, so preserve both canonical parameter names.
        if r.get("in") == 2 and "str" in r: r["str"]["str"]="u_1"
        if r.get("in") == 11 and "str" in r: r["str"]["str"]="u"
    args.candidate.parent.mkdir(parents=True,exist_ok=True)
    candidate_rows = output + helpers + suffix
    args.candidate.write_text("".join(json.dumps(r,separators=(",",":"))+"\n" for r in candidate_rows))
    args.control.parent.mkdir(parents=True,exist_ok=True)
    args.control.write_text("".join(json.dumps(r,separators=(",",":"))+"\n" for r in canon))
    print(json.dumps({"alternate_records":len(alt),"canonical_records":len(canon),"candidate_records":len(candidate_rows),"fresh_ids":next_id},sort_keys=True))
if __name__ == "__main__": main()
