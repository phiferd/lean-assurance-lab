"""Compatibility context for legacy stateful host-evidence tests."""
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def portable_validation():
    from lib import stateful_validation_pilot as stateful
    from lib import trust_assumption_pilot_r2 as trust
    from lib.trust_assumption_pilot_r3 import rebuild_result as portable_trust_rebuild

    old_source_check = stateful.source_check
    old_trust_rebuild = trust.rebuild_result

    def trust_rebuild(observation_bindings, root=trust.ROOT):
        expected = [
            str(trust.BASE / f"attempt-{index}/observation.json")
            for index in range(2)
        ]
        synthetic = (
            root != trust.ROOT
            and [binding.get("path") for binding in observation_bindings] == expected
        )
        return portable_trust_rebuild(
            observation_bindings, root, synthetic_fixture=synthetic,
        )

    def recorded_source_check():
        source = stateful.read(stateful.SOURCE)
        stateful.require(
            source["source_commit"] == "d8b18978322de05a8f3dba51ef03cf5461676c17",
            "source revision",
        )
        stateful.require(
            source["scientific_contract"] == stateful.bind(stateful.CONTRACT),
            "scientific input changed",
        )
        for row in [
            source["scientific_contract"], source["review"],
            source["runtime_inventory"], *source["sources"],
        ]:
            stateful.verify(row)
        for row in source["host_tools"]:
            stateful.require(
                Path(row["path"]).is_absolute()
                and len(row["sha256"]) == 64
                and all(c in "0123456789abcdef" for c in row["sha256"]),
                "invalid recorded host tool identity",
            )
        return source

    stateful.source_check = recorded_source_check
    trust.rebuild_result = trust_rebuild
    try:
        yield
    finally:
        stateful.source_check = old_source_check
        trust.rebuild_result = old_trust_rebuild
