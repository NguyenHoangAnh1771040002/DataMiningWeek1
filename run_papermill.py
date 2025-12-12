import papermill as pm
import os
import datetime as dt
import shutil
import re

import pandas as pd

from papermill.exceptions import PapermillExecutionError

os.makedirs("notebooks/runs", exist_ok=True)

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


def _categorize_item(desc: str) -> str:
    if desc is None:
        return "Other"
    s = str(desc).strip().upper()
    if not s:
        return "Other"

    rules = [
        ("Christmas", ["CHRISTMAS", "XMAS", "SANTA", "REINDEER", "SNOW", "TREE", "NOEL"]),
        ("Home Decor", ["DECOR", "DECORATION", "HANGING", "LANTERN", "CANDLE", "CANDLES", "HEART", "LIGHT", "MIRROR", "BUNTING"]),
        ("Kitchen & Dining", ["MUG", "CUP", "TEA", "TOWEL", "PLATE", "BOWL", "KITCHEN", "NAPKIN", "GLASS", "TRAY"]),
        ("Gift Wrap & Bags", ["BAG", "GIFT", "WRAP", "BOX", "RIBBON", "TAG", "CARD"]),
        ("Stationery & Crafts", ["PAPER", "NOTEBOOK", "PENCIL", "PEN", "STICKER", "CRAFT"]),
        ("Garden & Herbs", ["HERB", "GARDEN", "PLANT", "FLOWER"]),
    ]

    for cat, keywords in rules:
        if any(k in s for k in keywords):
            return cat
    return "Other"


def _rule_category(label: str) -> str:
    parts = [p.strip() for p in str(label).split(",") if p.strip()]
    if not parts:
        return "Other"
    cats = {_categorize_item(p) for p in parts}
    if len(cats) == 1:
        return list(cats)[0]
    return "Mixed"


def _category_insight_from_rules(rules_df: pd.DataFrame) -> dict:
    if rules_df is None or rules_df.empty:
        return dict(status="EMPTY")

    required = {"antecedents_str", "consequents_str", "lift", "confidence", "support"}
    if not required.issubset(set(rules_df.columns)):
        return dict(status="MISSING_COLUMNS")

    df = rules_df[["antecedents_str", "consequents_str", "lift", "confidence", "support"]].copy()
    df["ante_cat"] = df["antecedents_str"].apply(_rule_category)
    df["cons_cat"] = df["consequents_str"].apply(_rule_category)
    df["is_within_category"] = (df["ante_cat"] == df["cons_cat"]) & (~df["ante_cat"].isin(["Mixed"]))

    total_rules = int(len(df))
    within_rules = int(df["is_within_category"].sum())
    cross_rules = total_rules - within_rules

    pair_stats = (
        df.groupby(["ante_cat", "cons_cat"])
        .agg(
            n_rules=("lift", "size"),
            avg_lift=("lift", "mean"),
            avg_conf=("confidence", "mean"),
            median_support=("support", "median"),
        )
        .reset_index()
    )
    pair_stats.sort_values(["n_rules", "avg_lift"], ascending=[False, False], inplace=True)

    top_pairs = pair_stats.head(10)
    top_pairs_by_lift = (
        pair_stats[pair_stats["n_rules"] >= 5]
        .sort_values("avg_lift", ascending=False)
        .head(10)
    )

    cat_counts = (
        pd.concat(
            [
                df[["ante_cat"]].rename(columns={"ante_cat": "cat"}),
                df[["cons_cat"]].rename(columns={"cons_cat": "cat"}),
            ],
            ignore_index=True,
        )
        .value_counts("cat")
        .reset_index(name="appearances")
    )

    return dict(
        status="OK",
        total_rules=total_rules,
        within_rules=within_rules,
        cross_rules=cross_rules,
        within_rate=(within_rules / total_rules) if total_rules else 0.0,
        top_pairs=top_pairs,
        top_pairs_by_lift=top_pairs_by_lift,
        cat_counts=cat_counts,
    )


timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _cleanup_old_plot_dirs(current_plot_dir: str):
    reports_dir = "reports"
    try:
        if not os.path.isdir(reports_dir):
            return

        for name in os.listdir(reports_dir):
            if not name.startswith("plots_"):
                continue
            path = os.path.join(reports_dir, name)
            if not os.path.isdir(path):
                continue
            if os.path.normpath(path) == os.path.normpath(current_plot_dir):
                continue
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        return

plot_output_dir = f"reports/plots_{timestamp}"
os.makedirs(plot_output_dir, exist_ok=True)
os.environ["PLOT_OUTPUT_DIR"] = plot_output_dir

_cleanup_old_plot_dirs(plot_output_dir)


def _cleanup_old_sweep_artifacts():
    try:
        rules_dir = "data/processed"
        runs_dir = "notebooks/runs"

        exp_names = [e.get("name") for e in experiments if e.get("name") != "baseline"]
        exp_re = "(?:" + "|".join(map(re.escape, exp_names)) + ")"

        rules_pat = re.compile(rf"^rules_{exp_re}_\d{{8}}_\d{{6}}\.csv$")
        nb_pat = re.compile(rf"^apriori_modelling_{exp_re}_\d{{8}}_\d{{6}}\.ipynb$")

        if os.path.isdir(rules_dir):
            for name in os.listdir(rules_dir):
                if rules_pat.match(name):
                    path = os.path.join(rules_dir, name)
                    try:
                        os.remove(path)
                    except Exception:
                        pass

        if os.path.isdir(runs_dir):
            for name in os.listdir(runs_dir):
                if nb_pat.match(name):
                    path = os.path.join(runs_dir, name)
                    try:
                        os.remove(path)
                    except Exception:
                        pass
    except Exception:
        return


_cleanup_old_sweep_artifacts()

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
        params.update(
            dict(
                PLOT_TOP_LIFT=True,
                PLOT_TOP_CONF=True,
                PLOT_SCATTER=True,
                PLOT_NETWORK=True,
                PLOT_PLOTLY_NETWORK=False,
                PLOT_PLOTLY_SCATTER=False,
            )
        )

    if exp_name == "baseline":
        rules_output_path = "data/processed/rules_apriori_filtered.csv"
        notebook_output_path = "notebooks/runs/apriori_modelling_run.ipynb"
    else:
        rules_output_path = f"data/processed/rules_{exp_name}.csv"
        notebook_output_path = f"notebooks/runs/apriori_modelling_{exp_name}.ipynb"
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

# Category-level insight (Chủ đề 6) - phân tích trên baseline rules
try:
    baseline_rules_df = _read_rules_csv("data/processed/rules_apriori_filtered.csv")
    cat_result = _category_insight_from_rules(baseline_rules_df)

    lines.append("")
    lines.append("## 5. Chủ đề 6: Nhóm sản phẩm (Category-level Insight)")
    lines.append("")
    lines.append("Ghi chú: danh mục được gán theo keyword từ `Description` (heuristic) để phục vụ phân tích nhanh.")

    if cat_result.get("status") != "OK":
        lines.append("")
        lines.append(f"Không thể phân tích category-level insight (status={cat_result.get('status')}).")
    else:
        lines.append("")
        lines.append(f"- Tổng số luật (baseline): **{cat_result['total_rules']}**")
        lines.append(
            f"- Luật trong cùng danh mục (within-category): **{cat_result['within_rules']}** ({cat_result['within_rate']*100:.1f}%)"
        )
        lines.append(
            f"- Luật khác danh mục (cross-category): **{cat_result['cross_rules']}** ({(1-cat_result['within_rate'])*100:.1f}%)"
        )

        lines.append("")
        lines.append("### 5.1. Nhóm danh mục xuất hiện nhiều (tần suất xuất hiện trong luật)")
        lines.append("")
        for _, r in cat_result["cat_counts"].head(8).iterrows():
            lines.append(f"- **{r['cat']}**: {int(r['appearances'])}")

        lines.append("")
        lines.append("### 5.2. Top cặp danh mục theo số lượng luật")
        lines.append("")
        lines.append("| Antecedent category | Consequent category | #rules | avg_lift | avg_conf | median_support |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for _, r in cat_result["top_pairs"].iterrows():
            lines.append(
                "| "
                + str(r["ante_cat"])
                + " | "
                + str(r["cons_cat"])
                + " | "
                + str(int(r["n_rules"]))
                + " | "
                + f"{float(r['avg_lift']):.2f}"
                + " | "
                + f"{float(r['avg_conf']):.2f}"
                + " | "
                + f"{float(r['median_support']):.4f}"
                + " |"
            )

        lines.append("")
        lines.append("### 5.3. Top cặp danh mục theo avg_lift (lọc n_rules >= 5)")
        lines.append("")
        lines.append("| Antecedent category | Consequent category | #rules | avg_lift | avg_conf | median_support |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for _, r in cat_result["top_pairs_by_lift"].iterrows():
            lines.append(
                "| "
                + str(r["ante_cat"])
                + " | "
                + str(r["cons_cat"])
                + " | "
                + str(int(r["n_rules"]))
                + " | "
                + f"{float(r['avg_lift']):.2f}"
                + " | "
                + f"{float(r['avg_conf']):.2f}"
                + " | "
                + f"{float(r['median_support']):.4f}"
                + " |"
            )

        lines.append("")
        lines.append("### 5.4. Nhận định nhóm sản phẩm có tiềm năng marketing cao")
        lines.append("")
        lines.append("- Nhóm danh mục có nhiều luật within-category thường phù hợp để tạo **combo theo chủ đề** và trưng bày theo cụm.")
        lines.append("- Các cặp danh mục cross-category có avg_lift cao gợi ý cơ hội **cross-sell giữa nhóm** (ví dụ: đồ gói quà đi kèm đồ trang trí/quà tặng).")
except Exception:
    pass

with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

viz_report_path = "VISUALIZATION_REPORT.md"
viz_lines: list[str] = []
viz_lines.append("# Trực quan hoá kết quả Apriori")
viz_lines.append("")
viz_lines.append(f"Thời điểm chạy: `{timestamp}`")
viz_lines.append("")
viz_lines.append("Các biểu đồ được lưu tự động tại:")
viz_lines.append("")
viz_lines.append(f"- `{plot_output_dir}`")
viz_lines.append("")
viz_lines.append("## 1. Bar chart: Top luật theo Lift")
viz_lines.append("")
viz_lines.append(f"![Top rules by lift]({plot_output_dir}/bar_top_rules_by_lift.png)")
viz_lines.append("")
viz_lines.append("**Diễn giải ý nghĩa**")
viz_lines.append("")
viz_lines.append("- Lift đo mức độ mối quan hệ mạnh hơn ngẫu nhiên giữa vế trái và vế phải của luật.")
viz_lines.append("- Bar chart này giúp chọn các luật có lift cao để ưu tiên cho gợi ý mua kèm / combo / trưng bày gần nhau.")
viz_lines.append("- Khi đọc biểu đồ, nên kiểm tra thêm support để tránh chọn luật quá hiếm (khó áp dụng rộng).")
viz_lines.append("")
viz_lines.append("## 2. Scatter plot: Support vs Confidence (màu = Lift)")
viz_lines.append("")
viz_lines.append(f"![Support vs confidence]({plot_output_dir}/scatter_support_confidence_lift.png)")
viz_lines.append("")
viz_lines.append("**Diễn giải ý nghĩa**")
viz_lines.append("")
viz_lines.append("- Support cho biết luật xuất hiện thường xuyên đến mức nào trong toàn bộ hoá đơn (tính phổ biến).")
viz_lines.append("- Confidence cho biết xác suất mua vế phải khi đã mua vế trái (tính chắc chắn).")
viz_lines.append("- Màu (Lift) cho biết mức độ liên hệ vượt ngẫu nhiên; điểm càng đậm/thể hiện lift cao càng đáng chú ý.")
viz_lines.append("- Nhóm điểm ở vùng support vừa phải + confidence cao thường phù hợp để triển khai recommendation trên website/checkout.")
viz_lines.append("")
viz_lines.append("## 3. Network graph: Mạng lưới luật (antecedent → consequent)")
viz_lines.append("")
viz_lines.append(f"![Network rules]({plot_output_dir}/network_rules.png)")
viz_lines.append("")
viz_lines.append("**Diễn giải ý nghĩa**")
viz_lines.append("")
viz_lines.append("- Node là sản phẩm, cạnh có hướng thể hiện luật A → B.")
viz_lines.append("- Cụm node dày đặc gợi ý nhóm sản phẩm hay mua cùng, hữu ích cho bố trí kệ hàng hoặc tạo bộ combo.")
viz_lines.append("- Node có nhiều liên kết có thể xem như sản phẩm ‘hub’, phù hợp đặt ở vị trí nổi bật hoặc làm anchor cho cross-sell.")

with open(viz_report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(viz_lines) + "\n")

print(f"Đã chạy xong pipeline sweep. Report: {report_path}. Viz report: {viz_report_path}")
