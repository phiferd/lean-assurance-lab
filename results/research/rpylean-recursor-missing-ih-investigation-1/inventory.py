"""Print declaration metadata in file order for the source-locked Arena export."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys


def inventory(data):
    lock = json.loads(Path(__file__).with_name("work-record.json").read_text())
    fixture = "external/lean-kernel-arena/tests/rec-missing-ih.ndjson"
    digest = sha256(data).hexdigest()
    if digest != lock["sources"][fixture]["sha256"]:
        raise ValueError("The file differs from the source-locked export")

    names = {0: ""}
    declarations = []
    counts = Counter()
    shapes = Counter()
    lines = data.splitlines()
    for line_number, line in enumerate(lines, 1):
        row = json.loads(line)
        if "in" in row:
            part = row["str"] if "str" in row else row["num"]
            prefix = names[part["pre"]]
            suffix = part["str"] if "str" in row else str(part["i"])
            names[row["in"]] = f"{prefix}.{suffix}" if prefix else suffix
        elif "inductive" in row:
            group = row["inductive"]
            record = {"line": line_number, "kind": "inductive"}
            for category, fields in (
                ("types", ("numParams", "numIndices", "numNested")),
                ("ctors", ("cidx", "numParams", "numFields")),
                ("recs", ("numParams", "numIndices", "numMotives", "numMinors", "k")),
            ):
                rows = []
                for declaration in group[category]:
                    entry = {"name": names[declaration["name"]]}
                    entry.update({field: declaration[field] for field in fields})
                    if category == "recs":
                        rules = declaration["rules"]
                        entry["rules"] = [
                            {"ctor": names[r["ctor"]], "nfields": r["nfields"]}
                            for r in rules
                        ]
                        counts["rules"] += len(rules)
                        shapes[tuple(declaration[field] for field in fields)] += 1
                    rows.append(entry)
                record[category] = rows
                counts[category] += len(rows)
            declarations.append(record)
            counts["inductive_groups"] += 1
        else:
            for kind in ("def", "thm", "opaque", "axiom", "quot"):
                if kind in row:
                    declarations.append({"line": line_number, "kind": kind,
                                         "name": names[row[kind]["name"]]})
                    counts[kind] += 1
                    break
    return {"export_sha256": digest, "bytes": len(data), "lines": len(lines),
            "counts": counts, "recursor_shapes": [
                dict(zip(("numParams", "numIndices", "numMotives", "numMinors", "k"), key),
                     count=count) for key, count in sorted(shapes.items())
            ], "declarations": declarations}


if __name__ == "__main__":
    print(json.dumps(inventory(Path(sys.argv[1]).read_bytes()), indent=2, ensure_ascii=False))
