from pathlib import Path

from core.orchestrator.context import RunContext

from products.ade.tools.data_reader import DataReaderTool


def test_demo_data_reader_branded_cards() -> None:
    tool = DataReaderTool()
    run_ctx = RunContext(run_id="run_demo", product="ade", flow="ade_v1", payload={})
    step_ctx = run_ctx.new_step(step_id="read", step_type="tool", target="data_reader")

    result = tool.run({"dataset": "branded_cards_transactions"}, step_ctx)
    assert result.ok, result.error
    data = result.data or {}
    assert data.get("row_count") == 1000

    expected_columns = [
        "transaction_id",
        "account_id",
        "customer_id",
        "card_network",
        "card_type",
        "product",
        "txn_ts",
        "amount_inr",
        "currency",
        "merchant_name",
        "merchant_category",
        "merchant_city",
        "merchant_country",
        "channel",
        "auth_type",
        "status",
        "decline_reason",
        "is_international",
        "fx_rate",
        "amount_base_inr",
        "risk_score",
        "fraud_label",
        "device_id",
        "ip_country",
        "latitude",
        "longitude",
    ]
    assert data.get("columns") == expected_columns

    product_root = Path(__file__).resolve().parents[2]
    demo_path = product_root / "data" / "branded_cards_transactions.csv"
    assert demo_path.exists()
