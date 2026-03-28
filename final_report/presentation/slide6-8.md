# Nội dung thuyết trình chi tiết cho Slide 6, 7, 8

Dưới đây là kịch bản chi tiết và giải thích cặn kẽ (để bạn hiểu rõ bản chất và dễ dàng trả lời câu hỏi phản biện) dành cho phần thuyết trình của bạn.

---

## SLIDE 6: EXPLORATORY DATA ANALYSIS (EDA) & STATISTICS (Phân tích dữ liệu khám phá & Thống kê)

**Mục tiêu của slide này:** Cho khán giả thấy bức tranh tổng quan về dữ liệu thực tế sau khi đã làm sạch, những đặc trưng nào ảnh hưởng mạnh nhất đến giá nhà và xu hướng của thị trường.

### 🗣️ Kịch bản nói (Gợi ý):
"Chào thầy/cô và các bạn, tiếp nối phần xử lý dữ liệu, mình xin phép đi sâu vào phần Exploratory Data Analysis (EDA) - tức là Khám phá và thống kê dữ liệu. Mục đích của bước này là 'lắng nghe' xem dữ liệu đang kể câu chuyện gì trước khi đưa vào mô hình học máy.

Đầu tiên, khi nhìn vào phân phối giá nhà (Price Distribution), nhóm mình phát hiện dữ liệu bị lệch phải (right-skewed). Điều này rất hợp lý với thực tế vì đại đa số bất động sản trên thị trường nằm ở phân khúc trung cấp từ 1 đến 10 tỷ VNĐ. Trong khi đó, các bất động sản siêu cao cấp (vài chục đến cả trăm tỷ) thì rất ít nhưng giá lại cực cao, vô tình kéo dãn biểu đồ về bên phải.

Thứ hai, về sự khác biệt theo vùng miền (Regional Differences), biểu đồ histogram của nhóm cho thấy TP.HCM và Hà Nội có mức giá trung bình cao nhất và mức độ biến động giá (variance) cũng rất lớn. Lý do đơn giản: đây là hai lõi kinh tế, quỹ đất ngày càng cạn kiệt. Ngược lại, Đà Nẵng và Bình Dương cho thấy mặt bằng giá ổn định và thấp hơn đôi chút, phản ánh đúng tính chất của các thị trường đang phát triển hoặc tập trung vào nhu cầu ở thực (của chuyên gia/công nhân).

Và quan trọng nhất là phần Tương quan (Correlations). Không có gì ngạc nhiên khi Diện tích (Area) tỷ lệ thuận mạnh mẽ với Giá trị tài sản. Tuy nhiên, điểm đặc biệt nhóm tìm ra là **mối tương quan lên đến 0.80 giữa hệ thống hạ tầng tiện ích (như trường học, bệnh viện trong bán kính 1km) và giá nhà**. Điều này chứng minh bằng những con số cụ thể rằng: Người đi mua nhà không chỉ mua vài chục mét vuông gạch vữa, mà họ mua cả 'hệ sinh thái' xung quanh ngôi nhà đó. Càng nhiều tiện ích, giá trị càng được bù đắp."

### 🧠 Giải thích thêm (Để bạn hiểu sâu & Trả lời Q&A khi bị hỏi):
- **Tại sao lại lệch phải (Right-skewed) và nhóm xử lý nó thế nào?** Vì giá bất động sản không bao giờ có số âm, nhưng lại không có giới hạn trên (có những căn biệt thự hàng trăm tỷ). Trong code, nhóm phải dùng log-transform (lấy logarit tự nhiên của cột giá) để kéo biểu đồ phân phối trở về dạng Hình Chuông (Normal Distribution), giúp mô hình ML dự đoán chính xác hơn trên những căn nhà giá siêu cao.
- **Tại sao tính tương quan (Correlation Matrix / Heatmap) lại quan trọng tới vậy?** Để 1) Loại bỏ yếu tố **đa cộng tuyến** (multicollinearity) và 2) Chọn ra những features (đặc trưng) tốt nhất đưa vào mô hình. Ví dụ: Nếu "Khoảng cách tới trung tâm" và "Số trường học" tương quan quá mạnh với nhau, đôi khi ta chỉ cần giữ lại 1 để mô hình ML bớt nặng nề và phức tạp.

---

## SLIDE 7: MODELLING / REGRESSION ANALYSIS (Mô hình hóa / Phân tích hồi quy)

**Mục tiêu của slide này:** Giải thích quá trình chuyển đổi dữ liệu thành thuật toán dự đoán. Nêu bật sự khác biệt giữa mô hình tuyến tính cơ bản và các mô hình học máy phức tạp, để giải thích tại sao nhóm phải thử đến 15 mô hình.

### 🗣️ Kịch bản nói (Gợi ý):
"Sau khi đã hiểu rõ dữ liệu, chúng ta bước vào giai đoạn cốt lõi nhất: Mô hình hóa (Modelling). Để mô hình có thể học được, nhóm mình đã xây dựng một Preprocessing Pipeline (ống dẫn tiền xử lý dữ liệu) rất chặt chẽ. Dữ liệu được chia ngẫu nhiên theo tỷ lệ 80:20 (80% để huấn luyện - train, 20% để kiểm thử - test tránh gian lận). 

Đồng thời, nhóm áp dụng One-Hot Encoding để số hóa các biến chữ (ví dụ: biến tên Quận hoặc Loại hình nhà) và StandardScaler để co giãn các biến liên tục về cùng một hệ quy chiếu, giúp mô hình không bị 'ảo tưởng' rằng các số liệu lớn là quan trọng hơn số liệu nhỏ.

Ban đầu, để thiết lập một baseline (mốc cơ sở so sánh), nhóm sử dụng thuật toán **Hồi quy tuyến tính Ridge (Ridge Regression)**. Mô hình này giúp chúng ta thấy rõ 'trọng số' của từng yếu tố - ví dụ, nhà ở Quận trung tâm hoặc loại hình Biệt thự sẽ cộng thêm môt lượng tiền rất lớn vào thuật toán dự đoán giá. 
Tuy nhiên, R-squared (độ chính xác) của mô hình Ridge này chỉ lẹt đẹt ở mức 0.57. Tại sao lại thấp vậy? Bởi vì Hồi quy tuyến tính giả định mối quan hệ giữa các biến số và giá nhà là một đường thẳng. Trong khi thực tế thị trường bất động sản vô cùng phức tạp và là quan hệ phi tuyến (non-linear).

Nhận ra sự hạn chế đó, nhóm mình không dừng lại mà đã tiến hành lập trình thử nghiệm với **hơn 15 thuật toán Học máy (Machine Learning) khác nhau**. Tiêu biểu nhất là các mô hình dạng Cây Quyết định (Tree-based ensemble) như Random Forest, XGBoost, CatBoost hay LightGBM. Những mô hình dạng Cây này có khả năng tự động rẽ nhánh, bẻ cong và nắm bắt các mối quan hệ chéo cực kỳ phức tạp giữa các đặc tính mà con người và hàm tuyến tính không thể nhìn thấy được."

### 🧠 Giải thích thêm (Để bạn hiểu sâu & Trả lời Q&A khi bị hỏi):
- **Cụ thể One-Hot Encoding là gì mà phải dùng?** Máy tính không hiểu chữ "Quận 1" hay "Cầu Giấy". Nó chỉ hiểu số 0 và 1. One-hot sẽ tách cột "Quận" thành nhiều cột nhỏ chứa giá trị 0-1 (Ví dụ cột "Là_Quan_1", "Là_Cau_Giay"), để thuật toán đo đếm được sức ảnh hưởng của từng khu vực.
- **StandardScaler đóng vai trò gì?** Diện tích dao động từ 15-1000m², trong khi số lượng trường học quanh đó chỉ từ 1-20. Nếu không Scaler chuẩn hóa trước, cỗ máy sẽ lầm tưởng "Diện tích to nên diện tích là vua, bỏ qua số trường học". Scaler ép mọi tọa độ về cùng một phổ dao động.
- **Tại sao Ridge Regression lại tính ra R2 có 0.57?** R2=0.57 nghĩa là mô hình Ridge chỉ giải thích được 57% nguyên nhân tăng giảm của giá nhà. Lý do là giá nhà thay đổi phi tuyến. Ví dụ: Từ khoảng cách 1km đến trung tâm giảm xuống 0.5km thì giá rẽ sóng tăng đột biến, chứ không tăng đều 1 đường thẳng như từ 10km xuống 9.5km. Thuật toán dạng Cây (Tree-based) mới giải quyết được góc cua gắt này.

---

## SLIDE 8: KEY RESULTS & VISUALIZATIONS (Kết quả chính & Trực quan hóa)

**Mục tiêu của slide này:** Chốt lại đâu là thuật toán chiến thắng cuối cùng mang lại hiệu suất cao nhất và demo cách mô hình được đưa vào thực tế (ứng dụng Web) để người dùng cuối sử dụng như thế nào.

### 🗣️ Kịch bản nói (Gợi ý):
"Thưa thầy cô và các bạn, qua quá trình tinh chỉnh và đánh giá liên tục 15 mô hình khác nhau, 'nhà vô địch' của dự án nhóm 3 chính là thuật toán **Extra Trees (hay còn gọi là Extremely Randomized Trees)**. 

Mô hình này đã đạt được điểm số R-squared cao nhất là 0.84 trên dữ liệu kiểm thử (Test set), đồng nghĩa với việc mô hình dự đoán chính xác và bao quát được 84% sức mạnh biến động của giá nhà. Đồng thời biểu đồ cho thấy error rates (sai số) của Extra Trees được nén xuống mức thấp nhất. Nó thậm chí vượt qua cả những thuật toán boosting nổi đình nổi đám nhất hiện nay như XGBoost hay LightGBM.

Tuy nhiên, nhóm hiểu rằng: 'Một mô hình tốt sẽ trở nên hoàn toàn vô nghĩa nếu nó chỉ nằm chết trên các file code Jupyter Notebook'. Vì vậy, thành quả tự hào nhất của nhóm là đã đóng gói (deploy) mô hình này thành một **Ứng dụng Web tương tác thực tế bằng framework Streamlit**. 

Luồng hoạt động của app cực kỳ trực quan và sát với thực tế, các bạn có thể nhìn lên màn hình: 
1. Người mua nhà hoặc nhà đầu tư chỉ cần truy cập trang Web do nhóm làm, nhấn chọn vào một vị trí (tọa độ GPS) bất kỳ trên bản đồ Folium.
2. Ngay lập tức, hệ thống ngầm chạy API kết nối đến máy chủ OpenStreetMap để quét lưới và đếm số lượng trường học, bệnh viện, nhà hàng... xung quanh vị trí đó theo thời gian thực.
3. Dữ liệu không gian này sẽ cùng với thông số ban đầu (diện tích, pháp lý...) được đẩy thẳng vào mô hình Extra Trees đã huấn luyện sẵn.
4. Cuối cùng, kết quả trả về cho người dùng là một mức giá dự đoán tối ưu một cách chớp nhoáng trên màn hình. 

Sản phẩm này không chỉ dừng lại là một bài tập nghiên cứu môn học, mà hoàn toàn chứng minh được tiềm năng thương mại hóa thành một hệ thống định giá tự động (AVM - Automated Valuation Model) cho thị trường Real Estate (Bất động sản)."

### 🧠 Giải thích thêm (Để bạn hiểu sâu & Trả lời Q&A khi bị hỏi):
- **Phản biện giả định: Extra Trees là gì và tại sao lại tốt hơn Random Forest/XGBoost ở bài này?** 
Extra Trees (Extremely Randomized Trees) tương tự Random Forest nhưng thay vì đi tính toán để chọn ngưỡng cắt (split) tốt nhất nhằm chia nhánh cây, nó lại chọn "hoàn toàn ngẫu nhiên" các điểm bị cắt. 
Nghe có vẻ vô lý, nhưng chính việc cắt ngẫu nhiên (adding extreme randomness) này lại giúp Extra Trees giảm thiểu tối đa hiện tượng "học vẹt" (Overfitting - tức là học thuộc lòng Data Train mà làm bài Test kém) một cách cực tốt trên những bộ dữ liệu cực kỳ ngẫu nhiên và nhiễu (noisy) như báo giá nhà đất ở Việt Nam (vì chủ nhà nhiều lúc thích hét giá vô tội vạ).
- **Câu hỏi logic: Streamlit + API Folium bản đồ ngầm định giá thế nào?** 
Streamlit giúp code python hiển thị ra thành giao diện trang hiển web. Folium giúp chèn Google Maps/OpenstreetMap vào web. 
Khi user lấy chuột click vào bản đồ `->` Web lấy được tọa độ (Lat, Long). 
Từ tọa độ (Lat, Long) đó, Backend Python chạy gọi API sang hệ thống bản đồ để hỏi câu lệnh "Xung quanh (Lat,Long) này bán kính 1km có bao nhiêu trường học?". 
Có được số lượng trường học tiện ích `->` Hệ thống bốc số diện tích user gõ (vd: 50m2, 3 tầng) `->` Nạp mớ hỗn độn đó vào file thuật toán đã huấn luyện (`.pkl`) `->` Tiên đoán ra giá tiền VND/m2.
