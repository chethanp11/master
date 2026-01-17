from products.ade.tools.context_pack_builder import ContextPackInput, build_context_pack


def test_context_pack_builder_fields() -> None:
    payload = ContextPackInput(
        dataset_id="sample.csv",
        columns=["date", "value"],
        rows=[["2024-01-01", 10], ["2024-01-02", None]],
    )
    result = build_context_pack(payload)
    pack = result.context_pack
    assert pack.dataset_profile["dataset_id"] == "sample.csv"
    assert "coverage" in pack.model_dump(mode="json")
    assert pack.evidence_refs
