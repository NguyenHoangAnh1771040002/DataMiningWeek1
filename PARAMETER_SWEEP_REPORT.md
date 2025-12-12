# Thử nghiệm & phân tích tham số Apriori

Thời điểm chạy: `20251212_154315`

## 1. Bảng tổng hợp kết quả

| Experiment | status | min_support | min_confidence | min_lift | #rules | median_support | mean_confidence | median_lift | max_lift |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | OK | 0.0100 | 0.3000 | 1.2000 | 1794 | 0.0123 | 0.5352 | 9.7275 | 74.5670 |
| support_low | OK | 0.0050 | 0.3000 | 1.2000 | 24255 | 0.0059 | 0.5539 | 11.1187 | 101.9474 |
| support_high | OK | 0.0200 | 0.3000 | 1.2000 | 175 | 0.0233 | 0.4987 | 7.4949 | 27.2003 |
| conf_low | OK | 0.0100 | 0.2000 | 1.2000 | 2445 | 0.0122 | 0.4591 | 8.4478 | 74.5670 |
| conf_high | OK | 0.0100 | 0.5000 | 1.2000 | 944 | 0.0120 | 0.6605 | 12.4659 | 74.5670 |
| lift_low | OK | 0.0100 | 0.3000 | 1.1000 | 1794 | 0.0123 | 0.5352 | 9.7275 | 74.5670 |
| lift_high | OK | 0.0100 | 0.3000 | 1.5000 | 1794 | 0.0123 | 0.5352 | 9.7275 | 74.5670 |

## 2. Một vài luật tiêu biểu (top theo Lift)

- **baseline**: HERB MARKER PARSLEY, HERB MARKER ROSEMARY → HERB MARKER THYME
- **support_low**: CHRISTMAS TREE HEART DECORATION, CHRISTMAS TREE STAR DECORATION → CHRISTMAS TREE DECORATION WITH BELL
- **support_high**: WOODEN HEART CHRISTMAS SCANDINAVIAN → WOODEN STAR CHRISTMAS SCANDINAVIAN
- **conf_low**: HERB MARKER PARSLEY, HERB MARKER ROSEMARY → HERB MARKER THYME
- **conf_high**: HERB MARKER PARSLEY, HERB MARKER ROSEMARY → HERB MARKER THYME
- **lift_low**: HERB MARKER PARSLEY, HERB MARKER ROSEMARY → HERB MARKER THYME
- **lift_high**: HERB MARKER PARSLEY, HERB MARKER ROSEMARY → HERB MARKER THYME

## 2.1. Experiment bị lỗi (nếu có)

Không có experiment nào bị lỗi.

## 3. Nhận xét về sự thay đổi kết quả

- **Giảm min_support**: `#rules` 1794 → 24255 (+22461). Median support: 0.0123 → 0.0059. Mean confidence: 0.5352 → 0.5539. Median lift: 9.7275 → 11.1187.
- **Tăng min_support**: `#rules` 1794 → 175 (-1619). Median support: 0.0123 → 0.0233. Mean confidence: 0.5352 → 0.4987. Median lift: 9.7275 → 7.4949.
- **Giảm min_confidence**: `#rules` 1794 → 2445 (+651). Median support: 0.0123 → 0.0122. Mean confidence: 0.5352 → 0.4591. Median lift: 9.7275 → 8.4478.
- **Tăng min_confidence**: `#rules` 1794 → 944 (-850). Median support: 0.0123 → 0.0120. Mean confidence: 0.5352 → 0.6605. Median lift: 9.7275 → 12.4659.
- **Giảm min_lift**: `#rules` 1794 → 1794 (+0). Median support: 0.0123 → 0.0123. Mean confidence: 0.5352 → 0.5352. Median lift: 9.7275 → 9.7275.
- **Tăng min_lift**: `#rules` 1794 → 1794 (+0). Median support: 0.0123 → 0.0123. Mean confidence: 0.5352 → 0.5352. Median lift: 9.7275 → 9.7275.

## 4. File output

- **baseline**: rules=`data/processed/rules_apriori_filtered.csv`, notebook=`notebooks/runs/apriori_modelling_run.ipynb`
- **support_low**: rules=`data/processed/sweeps/rules_support_low_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_support_low_20251212_154315.ipynb`
- **support_high**: rules=`data/processed/sweeps/rules_support_high_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_support_high_20251212_154315.ipynb`
- **conf_low**: rules=`data/processed/sweeps/rules_conf_low_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_conf_low_20251212_154315.ipynb`
- **conf_high**: rules=`data/processed/sweeps/rules_conf_high_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_conf_high_20251212_154315.ipynb`
- **lift_low**: rules=`data/processed/sweeps/rules_lift_low_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_lift_low_20251212_154315.ipynb`
- **lift_high**: rules=`data/processed/sweeps/rules_lift_high_20251212_154315.csv`, notebook=`notebooks/runs/sweeps/apriori_modelling_lift_high_20251212_154315.ipynb`
