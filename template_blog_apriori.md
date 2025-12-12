# 📦 Case Study: Phân tích giỏ hàng với Apriori

## 👥 Thông tin Nhóm
- **Nhóm: 8** 
- **Thành viên:** 
  - Nguyễn Hoàng Anh
  - Nguyễn Văn Tiến
  - Phan Việt Hùng
  - Nguyễn Đoàn Ngọc Linh
- **Chủ đề: 6** 
- **Dataset:** Online Retail (UCI)

## Mục tiêu 
Mục tiêu của nhóm là:  
> Từ dữ liệu hoá đơn bán lẻ, nhóm tìm ra các **sản phẩm thường được mua cùng nhau**.
> Kết quả dùng để đề xuất **combo/cross-sell**, hỗ trợ **bố trí kệ hàng** và **khuyến mãi theo nhóm sản phẩm**.

## 1. Ý tưởng & Feynman Style
Giải thích lại bài toán theo cách **dễ hiểu nhất** (không technical):
- Apriori giúp trả lời câu hỏi: **"Khách mua món A thì hay mua kèm món B nào?"**
- Bài toán giỏ hàng phù hợp vì dữ liệu là các hoá đơn, mỗi hoá đơn giống như **một giỏ hàng** gồm nhiều sản phẩm.
- Ý tưởng: thuật toán sẽ tìm các nhóm sản phẩm xuất hiện cùng nhau đủ thường xuyên, rồi tạo luật dạng **A → B** để gợi ý mua kèm.

## 2. Quy trình Thực hiện

1) Load & làm sạch dữ liệu  
2) Tạo ma trận basket  
3) Áp dụng Apriori  
4) Trích xuất luật  
5) Trực quan hóa  
6) Phân tích insight  

## 3. Tiền xử lý Dữ liệu
- Những bước làm sạch:
  - Loại bỏ sản phẩm "rỗng"
  - Loại bỏ transaction bị cancel (InvoiceNo bắt đầu "C")
  - Loại bỏ số lượng âm
  - Lọc dữ liệu theo thị trường UK (United Kingdom)
  - Loại bỏ bản ghi có UnitPrice <= 0

- Thống kê nhanh:
  - Số giao dịch sau lọc: **18,021 hoá đơn (InvoiceNo)**
  - Số sản phẩm duy nhất: **4,007 sản phẩm (Description)**

## 4. Áp dụng Apriori
**Tham số sử dụng:**
- `min_support = 0.01`
- `min_threshold = 1.0` (metric = lift)
- `max_len = 3`

Ngoài cấu hình baseline, nhóm đã thử nghiệm thay đổi `min_support`, `min_confidence`, `min_lift` và tổng hợp trong `PARAMETER_SWEEP_REPORT.md`.

```python
from mlxtend.frequent_patterns import apriori, association_rules

frequent_itemsets = apriori(basket_df, min_support=0.01, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
rules.sort_values("lift", ascending=False, inplace=True)
rules.head()
```

## 5. Trực quan hóa (Visualization)
- Hình 1: **Bar chart Top luật theo Lift** (ưu tiên các luật có quan hệ mạnh hơn ngẫu nhiên)
  - Ý nghĩa: giúp chọn các cặp/nhóm sản phẩm phù hợp để **combo** hoặc **trưng bày gần nhau**.
- Hình 2: **Scatter plot Support vs Confidence (màu = Lift)** (nhìn trade-off giữa phổ biến và độ chắc chắn)
  - Ý nghĩa: hỗ trợ chọn luật vừa **đủ phổ biến (support)** vừa **đáng tin (confidence)** và có **lift tốt**.

Ghi chú: ảnh và diễn giải chi tiết được tổng hợp trong `VISUALIZATION_REPORT.md`.


## 6. Insight từ Kết quả
**Insight #1:**  
Nếu khách mua nhóm sản phẩm **HERB MARKER** (ví dụ PARSLEY/ROSEMARY) thì khả năng mua thêm **THYME** rất cao.  
Hành động: tạo **combo gia vị/đồ trang trí chủ đề herb** hoặc gợi ý “mua kèm THYME” ngay trên trang giỏ hàng.

**Insight #2:**  
Khi giảm `min_support` xuống 0.005, số luật tăng mạnh (1794 → 24255).  
Hành động: dùng cấu hình này để **khám phá ý tưởng** (brainstorm) nhưng khi triển khai nên quay về cấu hình chặt hơn để tránh luật quá hiếm.

**Insight #3:**  
Khi tăng `min_support` lên 0.02, số luật giảm rất mạnh (1794 → 175) và các luật còn lại thường phổ biến hơn.  
Hành động: ưu tiên các luật ở cấu hình này để làm **khuyến mãi đại trà** (áp dụng cho nhiều đơn hàng).

**Insight #4:**  
Khi tăng `min_confidence` lên 0.5, số luật giảm (1794 → 944) nhưng confidence trung bình tăng (0.5352 → 0.6605).  
Hành động: dùng các luật này cho **recommendation tại checkout** vì “tỉ lệ mua kèm” cao hơn.

**Insight #5:**  
Một số luật theo mùa xuất hiện rõ ở cấu hình `support_low` (ví dụ nhóm **CHRISTMAS TREE ... DECORATION**).  
Hành động: gom nhóm sản phẩm theo mùa và chạy **campaign theo mùa** (bundle trang trí Noel, trưng bày theo chủ đề).

**Insight #6 (Chủ đề 6 - Category-level):**  
Nhóm gán **danh mục sản phẩm** từ `Description` bằng keyword (ví dụ: `Christmas`, `Home Decor`, `Kitchen & Dining`, `Gift Wrap & Bags`, ...). Sau đó so sánh:
- Luật **trong cùng danh mục** (within-category): phù hợp để tạo **combo theo chủ đề** và trưng bày theo cụm.
- Luật **khác danh mục** (cross-category): phù hợp để triển khai **cross-sell giữa nhóm** (ví dụ nhóm gói quà đi kèm nhóm quà tặng/trang trí).

Nhận định: danh mục có tiềm năng marketing cao thường là danh mục xuất hiện nhiều trong luật và/hoặc có các cặp danh mục với **avg_lift** cao (tức là mua kèm vượt ngẫu nhiên).

## 7. Kết luận & Đề xuất Kinh doanh
- Gợi ý cross-sell: dùng các luật confidence cao để gợi ý “mua kèm” trên trang giỏ hàng/checkout.
- Gợi ý sắp xếp hàng trên kệ: đặt gần nhau các sản phẩm nằm trong cùng cụm (xem network graph) để tăng khả năng mua kèm.
- Gợi ý khuyến mãi theo mùa: dùng các luật nổi bật theo chủ đề (ví dụ Noel) để tạo combo theo mùa.

- Gợi ý theo danh mục (Chủ đề 6): thiết kế **campaign theo nhóm sản phẩm** (category) và ưu tiên các cặp danh mục có mức kết hợp cao (lift cao) để tối ưu ngân sách marketing.


## 8. Link Code & Notebook
- Notebook: `notebooks/runs/apriori_modelling_run.ipynb`
- Repo: https://github.com/NguyenHoangAnh1771040002/DataMiningWeek1

## 9. Slide trình bày
- Link Slide: 


