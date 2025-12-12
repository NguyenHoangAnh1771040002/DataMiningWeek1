# Shopping Cart Analysis

Phân tích dữ liệu bán lẻ để tìm ra mối quan hệ giữa các sản phẩm thường được mua cùng nhau bằng các kỹ thuật **Association Rule Mining** (Apriori). Project triển khai pipeline đầy đủ từ xử lý dữ liệu → phân tích → khai thác luật → sinh báo cáo.

---

## Features

- Làm sạch dữ liệu & xử lý giá trị lỗi
- Xây dựng basket matrix (transaction × product)
- Khai phá tập mục phổ biến (Frequent itemsets)
- Sinh luật kết hợp (Association Rules)
- Các chỉ số:
  - Support
  - Confidence
  - Lift
- Visualization với:
  - bar chart
  - scatter plot
  - network graph
  - interactive Plotly
- Tự động hóa pipeline bằng **Papermill**
- Category-level Insight (Chủ đề 6): gán danh mục sản phẩm (heuristic theo keyword) và so sánh kết hợp within-category vs cross-category

---

## Project Structure

```text
DataMiningWeek1/
├── data/
│   ├── raw/
│   │   └── online_retail.csv
│   └── processed/
│       ├── cleaned_uk_data.csv
│       ├── basket_bool.parquet
│       ├── rules_apriori_filtered.csv
│       └── rules_<experiment>.csv
│
├── notebooks/
│   ├── preprocessing_and_eda.ipynb
│   ├── basket_preparation.ipynb
│   ├── apriori_modelling.ipynb
│   └── runs/
│       ├── preprocessing_and_eda_run.ipynb
│       ├── basket_preparation_run.ipynb
│       ├── apriori_modelling_run.ipynb
│       └── apriori_modelling_<experiment>.ipynb
│
├── src/
│   └── apriori_library.py
│
├── run_papermill.py
├── PARAMETER_SWEEP_REPORT.md
├── VISUALIZATION_REPORT.md
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone <your_repo_url>
cd DataMiningWeek1
pip install -r requirements.txt
```

## Data Preparation

Đặt file gốc vào:

```bash
data/raw/online_retail.csv
```

File output sẽ được sinh tự động vào:

```bash
data/processed/
```

## Run Pipeline (Recommended)

Chạy toàn bộ pipeline (bao gồm **sweep tham số**) chỉ với 1 lệnh:

```bash
python run_papermill.py
```

Kết quả baseline sinh ra:

```bash
data/processed/cleaned_uk_data.csv
data/processed/basket_bool.parquet
data/processed/rules_apriori_filtered.csv
notebooks/runs/apriori_modelling_run.ipynb
```

Kết quả sweep (theo từng cấu hình) được lưu vào:

```bash
data/processed/rules_<experiment>.csv
notebooks/runs/apriori_modelling_<experiment>.ipynb
```

File báo cáo tổng hợp sweep:

```bash
PARAMETER_SWEEP_REPORT.md
```

Trong báo cáo này có thêm mục **Chủ đề 6: Nhóm sản phẩm (Category-level Insight)** gồm:

- So sánh tỷ lệ luật **trong cùng danh mục** vs **khác danh mục**
- Top cặp danh mục theo số lượng luật và các chỉ số (avg_lift, avg_conf, median_support)
- Nhận định danh mục có tiềm năng marketing cao

### Changing Parameters
Các tham số sweep đã được cấu hình sẵn trong `run_papermill.py` (mục `experiments`).

Các tham số chính:

```python
MIN_SUPPORT=0.01
MAX_LEN=3
FILTER_MIN_CONF=0.3
FILTER_MIN_LIFT=1.2
```

#### Tác động của các tham số

- **`MIN_SUPPORT`**: Giá trị này quyết định tần suất tối thiểu của các tập mục phổ biến. Giá trị thấp sẽ tạo ra nhiều tập mục hơn nhưng có thể làm tăng thời gian tính toán và tạo ra nhiều nhiễu. Giá trị cao sẽ lọc bớt các tập mục ít phổ biến nhưng có thể bỏ sót các tập mục quan trọng.

- **`FILTER_MIN_CONF`**: Ngưỡng tối thiểu cho độ tin cậy của luật. Giá trị cao đảm bảo các luật mạnh hơn nhưng có thể giảm số lượng luật được sinh ra.

- **`FILTER_MIN_LIFT`**: Giá trị này lọc các luật dựa trên chỉ số Lift, thể hiện mức độ mạnh mẽ của mối quan hệ so với ngẫu nhiên. Giá trị cao giúp chọn các luật có ý nghĩa hơn nhưng có thể loại bỏ các luật tiềm năng.

Việc điều chỉnh các tham số này cần cân nhắc giữa chất lượng và số lượng của các luật được sinh ra. Nên thử nghiệm với các giá trị khác nhau để tìm cấu hình phù hợp nhất với dữ liệu và mục tiêu phân tích.

### Visualization & Results
Notebook 03 hiển thị các biểu đồ sau:

Top luật theo Lift

Top luật theo Confidence

Scatter Support–Confidence–Lift

Network Graph giữa các sản phẩm

Biểu đồ Plotly tương tác

Bạn có thể export sang HTML:

```bash
jupyter nbconvert notebooks/runs/apriori_modelling_run.ipynb --to html
```

### Ứng dụng thực tế
Product recommendation

Cross-selling strategy

Combo gợi ý sản phẩm

Phân tích hành vi mua hàng

Sắp xếp sản phẩm tại siêu thị

### Tech Stack

| Công nghệ | Mục đích |
|----------|----------|
| Python | Ngôn ngữ chính |
| Pandas | Xử lý dữ liệu transaction |
| MLxtend | Apriori / FP-Growth association rules |
| Papermill | Chạy pipeline notebook tự động |
| Matplotlib & Seaborn | Visualization biểu đồ tĩnh |
| Plotly | Dashboard / biểu đồ tương tác |
| Jupyter Notebook | Môi trường notebook |

### Roadmap
 Thêm FP-Growth notebook (04)

 Streamlit dashboard để lọc luật


### Author
Project được thực hiện bởi:
Trang Le

📄 License
MIT — sử dụng tự do cho nghiên cứu, học thuật và ứng dụng nội bộ.
