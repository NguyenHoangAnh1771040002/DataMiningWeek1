import papermill as pm
import os
import datetime as dt

import pandas as pd

from papermill.exceptions import PapermillExecutionError

os.makedirs("notebooks/runs", exist_ok=True)
os.makedirs("notebooks/runs/sweeps", exist_ok=True)
os.makedirs("data/processed/sweeps", exist_ok=True)

# run_preprocessing_and_eda.py
pm.execute_notebook(
    "notebooks/preprocessing_and_eda.ipynb",
    "notebooks/runs/preprocessing_and_eda_run.ipynb",
    parameters=dict(
        DATA_PATH="data/raw/online_retail.csv",
        COUNTRY="United Kingdom",
        OUTPUT_DIR="data/processed",
        PLOT_REVENUE=False,         # tắt bớt plot khi chạy batch
        PLOT_TIME_PATTERNS=False,
        PLOT_PRODUCTS=False,
        PLOT_CUSTOMERS=False,
        PLOT_RFM=False,
    ),
    kernel_name="python3",
)

# run_basket_preparation.py

pm.execute_notebook(
    "notebooks/basket_preparation.ipynb",
    "notebooks/runs/basket_preparation_run.ipynb",
    parameters=dict(
        CLEANED_DATA_PATH="data/processed/cleaned_uk_data.csv",
        BASKET_BOOL_PATH="data/processed/basket_bool.parquet",
        INVOICE_COL="InvoiceNo",
        ITEM_COL="Description",
        QUANTITY_COL="Quantity",
        THRESHOLD=1,
    ),
    kernel_name="python3",
)


def _read_rules_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def _format_float(x) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.4f}"
    except Exception:
        return ""


timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

baseline_params = dict(
    BASKET_BOOL_PATH="data/processed/basket_bool.parquet",

    MIN_SUPPORT=0.01,
    MAX_LEN=3,

    METRIC="lift",
    MIN_THRESHOLD=1.0,

    FILTER_MIN_SUPPORT=0.01,
    FILTER_MIN_CONF=0.3,
    FILTER_MIN_LIFT=1.2,
    FILTER_MAX_ANTECEDENTS=2,
    FILTER_MAX_CONSEQUENTS=1,

    TOP_N_RULES=20,

    PLOT_TOP_LIFT=False,
    PLOT_TOP_CONF=False,
    PLOT_SCATTER=False,
    PLOT_NETWORK=False,
    PLOT_PLOTLY_NETWORK=False,
    PLOT_PLOTLY_SCATTER=False,
)

experiments = [
    dict(name="baseline", overrides=dict()),
    dict(name="support_low", overrides=dict(MIN_SUPPORT=0.005, FILTER_MIN_SUPPORT=0.005)),
    dict(name="support_high", overrides=dict(MIN_SUPPORT=0.02, FILTER_MIN_SUPPORT=0.02)),
    dict(name="conf_low", overrides=dict(FILTER_MIN_CONF=0.2)),
    dict(name="conf_high", overrides=dict(FILTER_MIN_CONF=0.5)),
    dict(name="lift_low", overrides=dict(FILTER_MIN_LIFT=1.1)),
    dict(name="lift_high", overrides=dict(FILTER_MIN_LIFT=1.5)),
]

summaries: list[dict] = []

for exp in experiments:
    exp_name = exp["name"]
    params = dict(baseline_params)
    params.update(exp["overrides"])

    if exp_name == "baseline":
        rules_output_path = "data/processed/rules_apriori_filtered.csv"
        notebook_output_path = "notebooks/runs/apriori_modelling_run.ipynb"
    else:
        rules_output_path = f"data/processed/sweeps/rules_{exp_name}_{timestamp}.csv"
        notebook_output_path = f"notebooks/runs/sweeps/apriori_modelling_{exp_name}_{timestamp}.ipynb"
    params["RULES_OUTPUT_PATH"] = rules_output_path

    status = "OK"
    error_msg = ""
    try:
        pm.execute_notebook(
            "notebooks/apriori_modelling.ipynb",
            notebook_output_path,
            parameters=params,
            kernel_name="python3",
        )
    except PapermillExecutionError as e:
        status = "FAILED"
        error_msg = str(e)
    except Exception as e:
        status = "FAILED"
        error_msg = repr(e)

    rules_df = _read_rules_csv(rules_output_path) if status == "OK" else pd.DataFrame()
    n_rules = int(len(rules_df))
    max_lift = rules_df["lift"].max() if (n_rules and "lift" in rules_df.columns) else None
    median_lift = rules_df["lift"].median() if (n_rules and "lift" in rules_df.columns) else None
    mean_conf = rules_df["confidence"].mean() if (n_rules and "confidence" in rules_df.columns) else None
    median_support = rules_df["support"].median() if (n_rules and "support" in rules_df.columns) else None
    top_rule = (
        rules_df.sort_values("lift", ascending=False).iloc[0]["rule_str"]
        if (n_rules and "lift" in rules_df.columns and "rule_str" in rules_df.columns)
        else ("(FAILED)" if status != "OK" else "")
    )

    summaries.append(
        dict(
            name=exp_name,
            MIN_SUPPORT=params.get("MIN_SUPPORT"),
            FILTER_MIN_CONF=params.get("FILTER_MIN_CONF"),
            FILTER_MIN_LIFT=params.get("FILTER_MIN_LIFT"),
            rules_path=rules_output_path,
            notebook_path=notebook_output_path,
            status=status,
            error_msg=error_msg,
            n_rules=n_rules,
            max_lift=max_lift,
            median_lift=median_lift,
            mean_conf=mean_conf,
            median_support=median_support,
            top_rule=top_rule,
        )
    )

report_path = "PARAMETER_SWEEP_REPORT.md"

baseline_summary = next((s for s in summaries if s["name"] == "baseline"), None)

lines: list[str] = []
lines.append("# Thử nghiệm & phân tích tham số Apriori")
lines.append("")
lines.append(f"Thời điểm chạy: `{timestamp}`")
lines.append("")
lines.append("## 1. Bảng tổng hợp kết quả")
lines.append("")
lines.append(
    "| Experiment | status | min_support | min_confidence | min_lift | #rules | median_support | mean_confidence | median_lift | max_lift |"
)
lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")

for s in summaries:
    lines.append(
        "| "
        + str(s["name"])
        + " | "
        + str(s.get("status", ""))
        + " | "
        + _format_float(s["MIN_SUPPORT"])
        + " | "
        + _format_float(s["FILTER_MIN_CONF"])
        + " | "
        + _format_float(s["FILTER_MIN_LIFT"])
        + " | "
        + str(s["n_rules"])
        + " | "
        + _format_float(s["median_support"])
        + " | "
        + _format_float(s["mean_conf"])
        + " | "
        + _format_float(s["median_lift"])
        + " | "
        + _format_float(s["max_lift"])
        + " |"
    )

lines.append("")
lines.append("## 2. Một vài luật tiêu biểu (top theo Lift)")
lines.append("")
for s in summaries:
    rule_txt = s.get("top_rule", "") or "(không có)"
    lines.append(f"- **{s['name']}**: {rule_txt}")

lines.append("")
lines.append("## 2.1. Experiment bị lỗi (nếu có)")
lines.append("")
failed_any = False
for s in summaries:
    if s.get("status") != "OK":
        failed_any = True
        msg = (s.get("error_msg") or "").replace("\n", " ")
        if len(msg) > 300:
            msg = msg[:300] + "..."
        lines.append(f"- **{s['name']}**: {msg}")
if not failed_any:
    lines.append("Không có experiment nào bị lỗi.")

lines.append("")
lines.append("## 3. Nhận xét về sự thay đổi kết quả")
lines.append("")

if baseline_summary is None:
    lines.append("Không tìm thấy baseline để so sánh.")
else:
    base_n = baseline_summary.get("n_rules", 0)

    def _compare(name: str, label: str):
        s = next((x for x in summaries if x["name"] == name), None)
        if s is None:
            return
        delta = s.get("n_rules", 0) - base_n
        sign = "+" if delta >= 0 else ""
        lines.append(
            f"- **{label}**: `#rules` {base_n} → {s.get('n_rules', 0)} ({sign}{delta}). "
            f"Median support: {_format_float(baseline_summary.get('median_support'))} → {_format_float(s.get('median_support'))}. "
            f"Mean confidence: {_format_float(baseline_summary.get('mean_conf'))} → {_format_float(s.get('mean_conf'))}. "
            f"Median lift: {_format_float(baseline_summary.get('median_lift'))} → {_format_float(s.get('median_lift'))}."
        )

    _compare("support_low", "Giảm min_support")
    _compare("support_high", "Tăng min_support")
    _compare("conf_low", "Giảm min_confidence")
    _compare("conf_high", "Tăng min_confidence")
    _compare("lift_low", "Giảm min_lift")
    _compare("lift_high", "Tăng min_lift")

    lines.append("")
    lines.append("## 4. File output")
    lines.append("")
    for s in summaries:
        lines.append(
            f"- **{s['name']}**: rules=`{s['rules_path']}`, notebook=`{s['notebook_path']}`"
        )

with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Đã chạy xong pipeline sweep. Report: {report_path}")
