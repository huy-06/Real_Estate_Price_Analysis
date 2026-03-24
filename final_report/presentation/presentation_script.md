# KỊCH BẢN THUYẾT TRÌNH CHI TIẾT VÀ BỘ CÂU HỎI Q&A DỰ PHÒNG (DỰ ÁN PHÂN TÍCH GIÁ BẤT ĐỘNG SẢN)

## PHẦN 1: KỊCH BẢN THUYẾT TRÌNH CHI TIẾT (SPEAKING SCRIPT)

**🗣️ Mở đầu chung:** 
"Dạ em chào thầy (cô) và các bạn. Hôm nay, đại diện cho Nhóm 3, em xin phép trình bày về dự án cuối kỳ của nhóm chúng em với đề tài: **Phân tích và Dự đoán Giá Bất Động Sản**."

### 📝 SLIDE 1: HOÀN CẢNH & BÀI TOÁN (BACKGROUND & PROBLEM CONTEXT)
*(Bấm chuyển slide)*
"Đầu tiên, hãy nói về bối cảnh. Như mọi người đều biết, thị trường bất động sản là một trong những trụ cột cốt lõi của nền kinh tế. Tuy nhiên, ở Việt Nam, có một thách thức rất lớn: **Làm sao để xác định được giá trị thực của một bất động sản?**"
*(Nhấn mạnh)* "Cực kỳ khó! Bởi vì giá cả bị chi phối bởi vô số yếu tố phức tạp như: vị trí, tính pháp lý, và các tiện ích xung quanh (như trường học, bệnh viện).
Nhận thấy 'nỗi đau' này của thị trường, nhóm chúng em đưa ra giải pháp: Ứng dụng **Khoa học Dữ liệu (Data Science)** để phân tích các tin đăng bán nhà đất, từ đó xây dựng một mô hình định giá khách quan nhất. Mục tiêu cuối cùng là giúp thị trường minh bạch hơn, hỗ trợ tối đa cho người mua và người bán ra quyết định."

### 📝 SLIDE 2: CÂU HỎI NGHIÊN CỨU & MỤC TIÊU (RESEARCH QUESTION & OBJECTIVES)
*(Bấm chuyển slide)*
"Từ bối cảnh đó, nhóm chúng em đặt ra một câu hỏi nghiên cứu cốt lõi: 
*'Làm thế nào để ứng dụng phân tích dữ liệu và học máy vào việc giải thích các yếu tố ảnh hưởng, từ đó dự đoán chính xác giá bất động sản dựa trên đặc điểm không gian và tiện ích xung quanh?'*

Để trả lời câu hỏi này, nhóm chia ra làm 2 mục tiêu chính:
1. **Mục tiêu Phân tích:** Tìm ra mối quan hệ ẩn giấu giữa giá tiền và các yếu tố vật lý/địa lý.
2. **Mục tiêu Dự đoán:** Xây dựng một mô hình Machine Learning đủ độ tin cậy, cung cấp một mức 'giá trần tham khảo', hỗ trợ quá trình thương lượng thực tế."

### 📝 SLIDE 3: TỔNG QUAN DỮ LIỆU (DATASET OVERVIEW)
*(Bấm chuyển slide)*
"Để mô hình học được, chúng em cần dữ liệu chất lượng. Dữ liệu của chúng em tập trung vào 4 thị trường sôi động nhất Việt Nam: **Hà Nội, Đà Nẵng, TP.HCM và Bình Dương**. 
Nguồn dữ liệu đến từ đâu ạ? Chúng em đào dữ liệu từ 2 nguồn chính:
- Một là: Thu thập tin đăng bán nhà từ trang web **batdongsan.com.vn**.
- Hai là: Kết nối với **OpenStreetMap (OSM)** để lấy thông tin về quy hoạch, tiện ích hạ tầng xung quanh ngôi nhà.

Tổng cộng, tập dữ liệu thô ban đầu cực kỳ khổng lồ với 39 biến (features), được chia làm 4 nhóm logic: Thông tin siêu dữ liệu (Metadata), Vị trí địa lý, Đặc điểm bất động sản (Diện tích, số tầng...), và Tiện ích ngoại khu."

### 📝 SLIDE 4: CHUẨN BỊ DỮ LIỆU & TRÍCH XUẤT BẰNG SQL (DATA PREPARATION & SQL EXTRACTION)
*(Bấm chuyển slide)*
"Phần công việc tốn kém thời gian nhất của chúng em chính là bước chuẩn bị dữ liệu. Dữ liệu thô cào từ web về 'rất bẩn'. 
- Chúng em đã dùng SQL và Python để chuẩn hóa text thành số (chẳng hạn giá tiền, diện tích). Xử lý đồng nhất tên các quận/huyện và loại bỏ các tin đăng trùng lặp.
- *(Nhấn mạnh)* Để mô hình không bị 'ảo' bởi các dữ liệu rác, chúng em đặt ra ranh giới lưới lọc: Chỉ giữ lại các bất động sản có giá từ **500 triệu đến 60 tỷ VNĐ**, và diện tích từ **15m² đến 1000m²**.
- Cuối cùng, thông qua các kỹ thuật chọn lọc đặc trưng (Feature Selection), nhóm đã rút gọn từ 39 biến thô xuống còn **17 biến quan trọng nhất**, có sức nặng dự đoán cao nhất (như Tổng Giá, Diện tích, Số tầng, Số trường học trong bán kính 1km...)."

### 📝 SLIDE 5: PHƯƠNG PHÁP & QUY TRÌNH (METHODOLOGY & WORKFLOW)
*(Bấm chuyển slide)*
"Về phương pháp thực hiện, nhóm tuân thủ nghiêm ngặt quy trình **OSEMN** trong Data Science. Tức là: Obtain (Thu thập) -> Scrub (Làm sạch) -> Explore (Khám phá EDA) -> Model (Mô hình hóa) -> và iNterpret (Diễn giải).

Về Tech-stack (Công nghệ), chúng em chủ yếu sử dụng ngôn ngữ **Python**. Cụ thể: Pandas, Numpy để xử lý; Matplotlib, Seaborn để vẽ biểu đồ trực quan; Thư viện Scikit-learn, CatBoost, XGBoost, LightGBM cho phần Machine Learning. Và cuối cùng, chúng em dùng Streamlit & Folium để đóng gói (deploy) thành một ứng dụng web thực tế."

### 📝 SLIDE 6: KHÁM PHÁ DỮ LIỆU EDA & THỐNG KÊ (EXPLORATORY DATA ANALYSIS)
*(Bấm chuyển slide)*
"Ở bước phân tích trực quan EDA, chúng em tìm ra nhiều insight rất thú vị.
- Về phân phối giá: Nó bị lệch phải mạnh, giá thực tế tập trung cực kỳ đặc ở phân khúc từ **1 đến 10 tỷ VNĐ**. 
- Về vùng miền: Bất động sản ở khu vực TP.HCM và Hà Nội có giá cao vượt trội và dao động rất mạnh, trong khi Đà Nẵng và Bình Dương ổn định hơn nhiều.
- Về hệ số tương quan: Nhóm phát hiện một điều đáng kinh ngạc: Độ tương quan giữa **Hạ tầng tiện ích (Trường học, Bệnh viện)** tỉ lệ thuận cực cao (lên tới 0.80) với sự hiện diện của các bất động sản. Không chỉ diện tích làm tăng giá, mà 'sống gần trường, gần viện' là một bảo chứng mạnh mẽ cho giá trị nhà ở."

### 📝 SLIDE 7: MÔ HÌNH HÓA (MODELLING / REGRESSION ANALYSIS)
*(Bấm chuyển slide)*
"Bước vào phần xây dựng mô hình, trước tiên chúng em setup một Pipeline xử lý: Điền khuyết dữ liệu (Missing value imputation), Mã hóa biến Categorical (One-Hot Encoding) và Scale dữ liệu. Tỉ lệ chia Train/Test là 80:20.

Đầu tiên, nhóm chạy thử một mô hình hồi quy cơ bản là **Ridge Regression**. Mô hình này đúng đắn ở việc xác định các quận trung tâm và phân khúc 'Biệt thự' mang lại giá trị cao (trọng số dương rất lớn). Tuy nhiên, vì thị trường nhà đất mang tính phi tuyến tính quá lớn, R-squared (R bình phương) của mô hình Ridge chỉ dừng lại ở **0.57** (tức là chỉ giải thích được 57% phương sai).
Không bỏ cuộc, chúng em đã thử nghiệm liên tục với **15 thuật toán Học máy (Machine Learning)** phức tạp hơn, từ các thuật toán cơ bản đến các mô hình Tree-based (Dựa trên cây quyết định) tiên tiến hiện nay để bắt được sự phi tuyến tính phức tạp của thị trường."

### 📝 SLIDE 8: KẾT QUẢ CỐT LÕI & TRỰC QUAN HÓA (KEY RESULTS & VISUALIZATIONS)
*(Bấm chuyển slide)*
"Và kết quả là? Trong 15 thuật toán đó, mô hình **Extra Trees (Extremely Randomized Trees)** đã vô địch. Mô hình này đạt điểm R-squared cao nhất lên đến **0.84** (có thể giải thích 84% sự biến động của giá) đồng thời có tỉ lệ sai số thấp nhất.

Để chứng minh tính ứng dụng, chúng em đã triển khai mô hình này lên một trang Web App tương tác bằng công nghệ Streamlit. *(Chỉ vào hình)* Như thầy cô (và các bạn) thấy trên màn hình, người dùng chỉ cần click vào một điểm bất kỳ trên bản đồ Folium. Ngầm bên dưới, một API sẽ ngay lập tức đếm số lượng tiện ích xung quanh đó, đẩy vào mô hình Extra Trees, và lập tức trả về giá trị dự đoán của căn nhà đó trong vài giây. Rất trực quan và thiết thực!"

### 📝 SLIDE 9: THẢO LUẬN, HẠN CHẾ & NHẬN ĐỊNH GÓC NHÌN (DISCUSSION, LIMITATIONS, AND INSIGHTS)
*(Bấm chuyển slide)*
"Từ kết quả này, chúng em đã định lượng thành công rằng: hạ tầng đô thị thực sự lạm phát giá trị bất động sản đến mức nào.
Thế nhưng, dự án cũng còn những giới hạn nhất định mà nhóm đúc rút được:
1. Dữ liệu đào tạo là 'Giá chào bán' trên web, đôi khi nó có sự chênh lệch (thương lượng xuống) so với hợp đồng giao dịch chốt cuối cùng.
2. Mô hình của chúng em hiện tại thiên về yếu tố 'cứng', chưa tính toán được các yếu tố 'mềm' như: Chất lượng nội thất, yếu tố Phong Thủy, hay Uy tín của chủ đầu tư.
- **Hướng phát triển tương lai**: Nhóm đề xuất sử dụng NLP (Xử lý ngôn ngữ tự nhiên) để đọc, phân tích cảm xúc và trích xuất các manh mối mềm từ chính đoạn text miêu tả của người bán."

### 📝 SLIDE 10: KẾT LUẬN & ỨNG DỤNG AI (CONCLUSION & AI USAGE REFLECTION)
*(Bấm chuyển slide)*
"Đúc kết lại, nhóm đã thực thi trọn vẹn một vòng đời dự án Khoa học dữ liệu: Từ số 0 đến một Website có mô hình chẩn đoán giá. 
Đặc biệt, trong khuôn khổ môn học, chúng em muốn có một góc nhìn nhỏ về việc sử dụng GenAI (như Gemini & ChatGPT). Trong dự án này, nhóm xem AI như một 'Pair-programmer'. AI hỗ trợ nhóm từ khâu lên ý tưởng chọn biến, debug những đoạn code báo lỗi, sửa script SQL phức tạp, cho đến việc căn chỉnh định dạng báo cáo LaTeX. Việc sử dụng AI không những làm tăng tốc độ dự án mà còn nâng cao đáng kể tiêu chuẩn chất lượng của chính nghiên cứu này.

Báo cáo của nhóm 3 đến đây là kết thúc. Trân trọng cảm ơn thầy (cô) và các bạn đã lắng nghe. Nhóm rất mong nhận được những góp ý cũng như các câu hỏi từ thầy cô ạ."

---

## PHẦN 2: BỘ CÂU HỎI Q&A DỰ PHÒNG CHUYÊN SÂU (15+ CÂU).
*(Bạn cần đọc kĩ phần này, nếu thầy cô hỏi vào những phần bạn CẮT BỎ trên slide, bạn sẽ lấy kiến thức ở đây bật lại)*

### 🏆 NHÓM 1: CÂU HỎI VỀ QUY TRÌNH THU THẬP DỮ LIỆU & TIỀN XỬ LÝ (DATA COLLECTION & PREPROCESSING)

**1. Các em cào dữ liệu (Crawling) bằng công cụ/thư viện gì? Quá trình cào có gặp khó khăn gì không?**
> **Trả lời (Gợi ý):** Dạ, nhóm sử dụng Python với thư viện BeautifulSoup và Selenium. Khó khăn lớn nhất là trang Batdongsan chặn IP nếu cào quá nhanh (mã lỗi 403 Forbidden). Chúng em phải xử lý bằng cách cấu hình file Scraper sleep ngẫu nhiên (random delay) khoảng 2-5 giây giữa các lượt request, và đổi User-Agent liên tục. Bên cạnh đó, dữ liệu HTML cũng thay đổi cấu trúc ở một vài trang làm code bị văng lỗi.

**2. Tại sao lại phải lấy dữ liệu từ OpenStreetMap (OSM) mà không chỉ dùng dữ liệu có sẵn trên web bất động sản? Cách các em lấy tiện ích xung quanh nhà thế nào?**
> **Trả lời:** Chào bán trên web thường người bán tự ghi "Gần trường, gần chợ" nhưng rất định tính và có thể phóng đại. Dữ liệu OSM là dữ liệu không gian khách quan định lượng được (tọa độ kinh độ/vĩ độ chính xác). Chúng em dựa vào tọa độ của bất động sản, dùng thuật toán tính khoảng cách địa lý (Haversine formula), vẽ một bán kính 1km xung quanh nhà, sau đó đếm số lượng trường học, bệnh viện, nhà hàng rơi vào trong vòng tròn đó (đây là kỹ thuật Spatial buffer).

**3. Tại sao lại lọc dữ liệu từ 500 triệu - 60 tỷ VND và diện tích 15m2 - 1000m2? Các số liệu ngoài ngưỡng này có phải là dữ liệu sai không?**
> **Trả lời:** Thưa thầy/cô, không hẳn là sai, nhưng nó là Outliers (dữ liệu ngoại lai). Các căn nhà dưới 500 triệu hoặc 15m2 thường là nhà ổ chuột/phòng trọ hoặc do người đăng gõ lộn số. Các căn trên 60 tỷ thường là lâu đài, building tòa nhà văn phòng, hoặc là một dạng bất động sản đặc thù bị chi phối bởi dòng tiền kinh doanh. Việc đưa outliers này vào sẽ làm mô hình bị nhiễu (noise) và kéo lệch đường hồi quy, nên nhóm quyết định focus vào phân khúc nhà ở/đất ở phổ thông và trung-cao cấp để mô hình thực tiễn nhất.

**4. Trong dataset của em chắc chắn có "Missing Value", các em xử lý thế nào?**
> **Trả lời:** Dạ đúng ạ. Tùy từng loại biến chúng em có cách xử lý khác nhau. Với dữ liệu dạng chuỗi (Categorical) như 'hướng nhà', 'giấy tờ pháp lý', chúng em thay thế vào bằng một nhóm 'Unknown' (Chưa rõ) thay vì bỏ đi, vì chính việc "Chưa rõ giấy tờ" bản thân nó cũng là một biến giải thích tại sao giá nhà bị rẻ hơn. Với dữ liệu dạng số (Numerical) như Số tầng hay Số phòng ngủ, nhóm dùng Kỹ thuật KNNImputer hoặc điền bằng giá trị trung vị (Median) dựa trên trục theo Tỉnh/Thành, vì mỗi tỉnh tính chất quy mô phòng ốc sẽ khác khau.

### 🏆 NHÓM 2: CÂU HỎI VỀ PHÂN TÍCH EXPLORATORY DATA (EDA) VÀ ĐẶC TRƯNG (FEATURE ENGINEERING)

**5. Vì sao dữ liệu phân phối giá lại bị Right-skewed (lệch phải)? Nó ảnh hưởng gì đến Model? Và các em giải quyết nó thế nào?**
> **Trả lời:** Dữ liệu lệch phải là tính đặc trưng phổ biến của thu nhập và tài sản. Hầu hết bất động sản trên thị trường nằm ở phân khúc vừa túi tiền (1-10 tỷ), chỉ có một số ít là siêu đắt (tail của biểu đồ dài kéo về bên phải). Nó làm cho các thuật toán Linear Regression bị sai lệch vì các model này giả định biến mục tiêu (target) tuân theo phân phối chuẩn (Normal Distribution). Giải pháp kỹ thuật nhóm cân nhắc dùng là thực hiện **Log Transformation (log1p)** lên biến `Price` để ép nó về dạng phân phối chuẩn trước khi đưa vào đào tạo, sau đó khi dự đoán xong thì dùng hàm Exponential biến đổi ngược giá trị lại.

**6. Biến (Features) nào là biến quan trọng nhất ảnh hưởng tới giá nhà trong mô hình của các em? (Feature Importance)**
> **Trả lời:** Dựa trên kết quả Feature Importance chiết xuất từ mô hình cây (Extra Trees), các biến có tác động mạnh nhất là: 1) Diện tích (Area), 2) Loại hình nhà (Loại Biệt thự hoặc Nhà mặt phố có trọng số cao hơn nhiều so với Nhà trong hẻm/Chung cư), và 3) Yếu tố địa lý như Tọa độ (Vĩ độ/Kinh độ) - vì vị trí phản ánh giá trị "đất vàng". Ngoài ra, số lượng tiện ích hạ tầng cấp 1 như Trường học và Bệnh viện trong bán kính gần cũng lọt vào top các biến mạnh.

**7. Làm sao để giải quyết vấn đề tự tương quan (Multicollinearity) giữa các biến? (Ví dụ nhà càng to thì số phòng ngủ tự động càng nhiều)**
> **Trả lời:** Dạ đúng ạ, hiện tượng Multicollinearity sẽ làm ảnh hưởng đến tính ổn định của các hàm hồi quy tuyến tính. Ban đầu nhóm tính dùng PCA (Principal Component Analysis) để giảm chiều, nhưng PCA làm mất khả năng diễn giải kinh tế của biến (không biết biến 1 biến 2 là gì nữa). Về sau, vì nhóm chọn chốt hạ dùng các mô hình Ensembles Tree-based (như Extra Trees, XGBoost) thì các mô hình Cây này hoàn toàn **miễn nhiễm** với đa cộng tuyến, mô hình sẽ tự chọn biến tối ưu để phân nhánh nên chúng em không cần loại bỏ các biến tương quan.

### 🏆 NHÓM 3: CÂU HỎI VỀ MACHINE LEARNING / XÂY DỰNG MÔ HÌNH (MODELLING)

**8. Thuật toán Extra Trees là gì? Tại sao nó lại vô địch mà không phải XGBoost hay Random Forest?**
> **Trả lời:** Extra Trees (Extremely Randomized Trees) là một phiên bản "anh em" của Random Forest. Tuy nhiên, nếu Random Forest tìm ngưỡng (threshold) phân chia dữ liệu tốt nhất để ngắt nhánh, thì Extra Trees bốc ngẫu nhiên (random) các ngưỡng cắt này. 
Lý do nó kết quả tốt hơn (R2=0.84) trên Local dataset của nhóm là vì: Bất động sản bị nhiễu rất nhiều (giá chào cao mồm, làm giá...). Việc thuật toán cắt cực kỳ ngẫu nhiên giúp mô hình "bớt học thuộc lòng" (giảm Overfitting) lên các dữ liệu nhiễu này, có tính tổng quát hóa tốt hơn. XGBoost có thể mạnh hơn nhưng vì XGBoost hoạt động theo cơ chế học lại các lỗi sai (Boosting), nếu bộ Data có nhiều nhiễu, XGBoost dễ bị Overfit (quá khớp) với dữ liệu nhiễu hơn là Extra Trees.

**9. Em nói tỷ lệ Train/Test là 80:20. Giả sử tập Test của em trúng toàn nhà rẻ, tập Train toàn nhà đắt thì sao? Làm sao em chắc R2=0.84 là do model tốt hay do ăn may?**
> **Trả lời:** Đây rủi ro về Data Leakage và Data Imbalance. Để khắc phục, nhóm không chỉ chia Random 80:20 thông thường, mà nhóm tích hợp **Cross-Validation (k-fold)** ví dụ k=5. Tức là huấn luyện và test đảo chéo 5 lần trên toàn bộ tập dữ liệu để lấy R-squared trung bình, đảm bảo mô hình không bị thiên lệch bởi cách chia dữ liệu ngẫu nhiên.

**10. R-squared = 0.84 nghĩa là gì trong bài toán này? Ngoài R-squared ra nhóm có dùng hàm Loss nào khác không?**
> **Trả lời:** R-squared = 0.84 nghĩa là mô hình của chúng em dùng các biến input (như Vị trí, Diện tích, Tiện ích) để GIẢI THÍCH ĐƯỢC 84% nguyên nhân sự biến động giá của một căn nhà. Chỉ còn 16% nguyên nhân là mô hình chưa hiểu được (ví dụ yếu tố tâm linh, nhà làm bằng gỗ quý, nợ ngân hàng bán gấp...). Ngoài R-squared, để đánh giá sai số THỰC TẾ, nhóm đánh giá bằng chỉ số **MAE (Mean Absolute Error)** (sai số tuyệt đối trung bình). Việc kết hợp cả hai giúp nhóm biết mô hình dự đoán trệch trung bình bao nhiêu triệu VNĐ.

**11. Có 15 thuật toán, các em dùng kỹ thuật gì để tối ưu siêu tham số (Hyperparameter Tuning)?**
> **Trả lời:** Với số lượng mô hình lớn, không thể dùng tay dò. Nhóm dùng kỹ thuật GridSearch (dạo toàn bộ mạng lưới) cho các mô hình cỏ, và dùng **RandomizedSearchCV** hoặc thư viện **Optuna** cho các mô hình phức tạp (như Boosting hoặc ExtraTrees) vì nó tiết kiệm chi phí tính toán nhưng vẫn tìm ra bộ tham số (như `n_estimators`, `max_depth`) tối ưu nhất ném R2 lên cao nhất.

### 🏆 NHÓM 4: ỨNG DỤNG BÁO CÁO, CÔNG NGHỆ & TƯƠNG LAI

**12. API kết nối để tính tiện ích ở sản phẩm Streamlit hoạt động ra sao? Nó có bắt người dùng chờ lâu không?**
> **Trả lời:** Giao diện Streamlit sử dụng package Folium để vẽ bản đồ tương tác. Khi người dùng click một chạm (Kinh độ X, Vĩ độ Y), ứng dụng sẽ tạo 1 query (truy vấn) API gọi trực tiếp sang máy chủ Overpass API của OpenStreetMap với khoảng cách Buffer 1km. Nó sẽ crawl Real-Time danh sách nhà thuốc, trường học, quán cafe... xung quanh đó, đếm số lượng, nhét vào Array làm Array Input cho mô hình `model.predict()`. Tổng thời gian phản hồi thường mất khoảng 2-4 giây do phụ thuộc tốc độ phản hồi của API OSM.

**13. Dự án này lấy giá "Chào bán" (Asking Price). Vậy mô hình bị phồng giá hơn thực tế (Transaction Price). Em phản biện thế nào?**
> **Trả lời:** Dạ đây là nhược điểm chí mạng của hầu hết mọi nghiên cứu Bất động sản công khai, vì Việt Nam chưa công khai giá hợp đồng công chứng. Tuy nhiên, giá 'Chào bán' có độ tương quan tịnh tiến với giá giao dịch thực (ví dụ giá thực luôn bằng 90-95% giá chào bán). Do đó, mô hình của nhóm vẫn hoàn thành tốt vai trò thiết lập một "Giá khởi điểm tham khảo" (Reference ceiling price), giúp người mua có căn cứ vững chắc để không bị ép giá quá đáng, và giúp sàn giao dịch khoanh vùng loại bỏ các tin đăng định giá lừa đảo / giả mạo trên hệ thống.

**14. Việc dùng AI (như em có đề cập ở Slide cuối) có bị xem là "lười biếng" không? (Câu hỏi vặn vẹo)**
> **Trả lời:** Nhóm tư duy AI không phải công cụ để làm thay, mà là "Kỹ sư đồng hành" (Pair-programmer / Assistant). Nhóm là người nắm quyền "Kiến trúc sư" (Architect), quyết định luồng đi (OSEMN), quyết định chọn biến gì, giữ bỏ biến nào về mặt kinh tế học. Khi đã có logic, nhóm giao cho AI viết các đoạn mã lệnh Regex xử lý Text cứng nhắc, hoặc vẽ format LaTeX phức tạp - vốn là những việc dùng sức bò (manual labor). Nhờ đó nhóm có dư dả không gian, thời gian để phân tích nguyên lý Toán Học và độ phù hợp thị trường của Project. AI giúp giải phóng trí não con người khỏi công việc tay chân.

