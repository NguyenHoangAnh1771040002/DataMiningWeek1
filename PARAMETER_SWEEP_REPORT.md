# Thử nghiệm & phân tích tham số Apriori

Thời điểm chạy: `20251212_183515`

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
- **support_low**: rules=`data/processed/rules_support_low.csv`, notebook=`notebooks/runs/apriori_modelling_support_low.ipynb`
- **support_high**: rules=`data/processed/rules_support_high.csv`, notebook=`notebooks/runs/apriori_modelling_support_high.ipynb`
- **conf_low**: rules=`data/processed/rules_conf_low.csv`, notebook=`notebooks/runs/apriori_modelling_conf_low.ipynb`
- **conf_high**: rules=`data/processed/rules_conf_high.csv`, notebook=`notebooks/runs/apriori_modelling_conf_high.ipynb`
- **lift_low**: rules=`data/processed/rules_lift_low.csv`, notebook=`notebooks/runs/apriori_modelling_lift_low.ipynb`
- **lift_high**: rules=`data/processed/rules_lift_high.csv`, notebook=`notebooks/runs/apriori_modelling_lift_high.ipynb`

## 5. Chủ đề 6: Nhóm sản phẩm (Category-level Insight)

Ghi chú: danh mục được gán theo keyword từ `Description` (heuristic) để phục vụ phân tích nhanh.

- Tổng số luật (baseline): **1794**
- Luật trong cùng danh mục (within-category): **1514** (84.4%)
- Luật khác danh mục (cross-category): **280** (15.6%)

### 5.1. Nhóm danh mục xuất hiện nhiều (tần suất xuất hiện trong luật)

- **Gift Wrap & Bags**: 2524
- **Other**: 470
- **Kitchen & Dining**: 165
- **Home Decor**: 159
- **Garden & Herbs**: 118
- **Mixed**: 73
- **Christmas**: 67
- **Stationery & Crafts**: 12

### 5.2. Top cặp danh mục theo số lượng luật

| Antecedent category | Consequent category | #rules | avg_lift | avg_conf | median_support |
|---|---|---:|---:|---:|---:|
| Gift Wrap & Bags | Gift Wrap & Bags | 1177 | 10.02 | 0.52 | 0.0128 |
| Other | Other | 163 | 15.78 | 0.49 | 0.0123 |
| Garden & Herbs | Garden & Herbs | 58 | 70.85 | 0.90 | 0.0105 |
| Mixed | Gift Wrap & Bags | 43 | 15.29 | 0.72 | 0.0109 |
| Kitchen & Dining | Kitchen & Dining | 42 | 26.45 | 0.69 | 0.0131 |
| Home Decor | Home Decor | 40 | 12.56 | 0.47 | 0.0115 |
| Gift Wrap & Bags | Other | 35 | 9.18 | 0.40 | 0.0120 |
| Christmas | Christmas | 28 | 19.47 | 0.56 | 0.0138 |
| Other | Gift Wrap & Bags | 28 | 10.37 | 0.45 | 0.0111 |
| Gift Wrap & Bags | Home Decor | 25 | 6.51 | 0.36 | 0.0122 |

### 5.3. Top cặp danh mục theo avg_lift (lọc n_rules >= 5)

| Antecedent category | Consequent category | #rules | avg_lift | avg_conf | median_support |
|---|---|---:|---:|---:|---:|
| Garden & Herbs | Garden & Herbs | 58 | 70.85 | 0.90 | 0.0105 |
| Stationery & Crafts | Stationery & Crafts | 6 | 27.20 | 0.57 | 0.0118 |
| Kitchen & Dining | Kitchen & Dining | 42 | 26.45 | 0.69 | 0.0131 |
| Other | Kitchen & Dining | 19 | 20.68 | 0.51 | 0.0121 |
| Christmas | Christmas | 28 | 19.47 | 0.56 | 0.0138 |
| Mixed | Other | 11 | 17.59 | 0.63 | 0.0104 |
| Other | Other | 163 | 15.78 | 0.49 | 0.0123 |
| Mixed | Gift Wrap & Bags | 43 | 15.29 | 0.72 | 0.0109 |
| Kitchen & Dining | Other | 24 | 15.23 | 0.51 | 0.0138 |
| Mixed | Kitchen & Dining | 18 | 14.97 | 0.76 | 0.0108 |

### 5.4. Nhận định nhóm sản phẩm có tiềm năng marketing cao

- Nhóm danh mục có nhiều luật within-category thường phù hợp để tạo **combo theo chủ đề** và trưng bày theo cụm.
- Các cặp danh mục cross-category có avg_lift cao gợi ý cơ hội **cross-sell giữa nhóm** (ví dụ: đồ gói quà đi kèm đồ trang trí/quà tặng).
