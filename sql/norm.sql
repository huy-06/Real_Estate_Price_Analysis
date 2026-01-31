/* 1. DỌN DẸP CÁC KÝ TỰ LẠ (ÉP KIỂU SANG CHUỖI TRƯỚC KHI XỬ LÝ) */
UPDATE Da_Nang
SET 
    -- Xử lý Diện tích
    area = REPLACE(REPLACE(REPLACE(LOWER(CAST(area AS NVARCHAR(MAX))), 'm2', ''), ',', '.'), ' ', ''),
    
    -- Xử lý Mặt tiền và Độ rộng đường
    frontage = REPLACE(REPLACE(REPLACE(LOWER(CAST(frontage AS NVARCHAR(MAX))), 'm', ''), ',', '.'), ' ', ''),
    road_width = REPLACE(REPLACE(REPLACE(LOWER(CAST(road_width AS NVARCHAR(MAX))), 'm', ''), ',', '.'), ' ', ''),
    
    -- Xử lý Số phòng ngủ và toilet (Lấy ký tự đầu tiên nếu là chuỗi)
    num_bedrooms = CASE 
        WHEN ISNUMERIC(LEFT(TRIM(CAST(num_bedrooms AS NVARCHAR(MAX))), 1)) = 1 
        THEN LEFT(TRIM(CAST(num_bedrooms AS NVARCHAR(MAX))), 1) 
        ELSE '0' END,
        
    num_toilets = CASE 
        WHEN ISNUMERIC(LEFT(TRIM(CAST(num_toilets AS NVARCHAR(MAX))), 1)) = 1 
        THEN LEFT(TRIM(CAST(num_toilets AS NVARCHAR(MAX))), 1) 
        ELSE '0' END;

/* 2. CHUYỂN CÁC GIÁ TRỊ KHÔNG PHẢI SỐ VỀ NULL ĐỂ TRÁNH LỖI CONVERT */
UPDATE Da_Nang
SET 
    area = CASE WHEN ISNUMERIC(area) = 1 THEN area ELSE NULL END,
    frontage = CASE WHEN ISNUMERIC(frontage) = 1 THEN frontage ELSE NULL END,
    road_width = CASE WHEN ISNUMERIC(road_width) = 1 THEN road_width ELSE NULL END,
    price_total = CASE WHEN ISNUMERIC(price_total) = 1 THEN price_total ELSE NULL END;

/* 3. LỆNH THAY ĐỔI KIỂU DỮ LIỆU AN TOÀN (DÙNG TRY_CAST) */
-- Chúng ta sẽ cập nhật trực tiếp những căn nhà có dữ liệu lỗi về 0 để ép kiểu thành công
UPDATE Da_Nang SET area = 0 WHERE area IS NULL;
UPDATE Da_Nang SET price_total = 0 WHERE price_total IS NULL;
UPDATE Da_Nang SET num_bedrooms = 0 WHERE num_bedrooms IS NULL;
UPDATE Da_Nang SET num_toilets = 0 WHERE num_toilets IS NULL;
UPDATE Da_Nang SET frontage = 0 WHERE frontage IS NULL;
UPDATE Da_Nang SET road_width = 0 WHERE road_width IS NULL;

-- Bây giờ mới thực hiện đổi kiểu dữ liệu cột
ALTER TABLE Da_Nang ALTER COLUMN area FLOAT;
ALTER TABLE Da_Nang ALTER COLUMN price_total FLOAT;
ALTER TABLE Da_Nang ALTER COLUMN num_bedrooms INT;
ALTER TABLE Da_Nang ALTER COLUMN num_toilets INT;
ALTER TABLE Da_Nang ALTER COLUMN frontage FLOAT;
ALTER TABLE Da_Nang ALTER COLUMN road_width FLOAT;

/* 4. CUỐI CÙNG: XÓA CÁC DÒNG GIÁ BẰNG 0 (VÌ KHÔNG DÙNG ĐỂ TRAIN ĐƯỢC) */
DELETE FROM Da_Nang WHERE price_total <= 0;






/* 1. CHUẨN HÓA CATEGORY (Xóa khoảng trắng thừa) */
UPDATE Da_Nang
SET category = TRIM(category);

/* 2. QUY HOẠCH LẠI LEGAL_STATUS (Gom 68 loại về 4 nhóm chính) */
UPDATE Da_Nang
SET legal_status = CASE 
    -- Nhóm 1: Đã có sổ (Nhóm giá trị cao nhất)
    WHEN legal_status LIKE N'%sổ đỏ%' 
      OR legal_status LIKE N'%sổ hồng%' 
      OR legal_status LIKE N'%sổ riêng%' 
      OR legal_status LIKE N'%sổ sẵn%' 
      OR legal_status LIKE N'%sổ hoàn công%'
      OR legal_status LIKE N'%Sổ chung%' -- Có thể tách nếu bạn muốn, nhưng thường vẫn xếp vào nhóm có sổ
      OR legal_status LIKE N'%đã có sổ%' 
      OR legal_status LIKE N'%Có sổ%' THEN N'Sổ đỏ/ Sổ hồng'

    -- Nhóm 2: Hợp đồng (Đang chờ sổ hoặc pháp lý dự án)
    WHEN legal_status LIKE N'%HĐMB%' 
      OR legal_status LIKE N'%Hợp đồng%' 
      OR legal_status LIKE N'%Văn bản%' 
      OR legal_status LIKE N'%VBTT%' 
      OR legal_status LIKE N'%đang chờ%' THEN N'Hợp đồng mua bán'

    -- Nhóm 3: Vi bằng / Giấy tờ tay (Rủi ro cao)
    WHEN legal_status LIKE N'%vi bằng%' 
      OR legal_status LIKE N'%Công chứng%' THEN N'Vi bằng/ Công chứng'

    -- Nhóm 4: Các loại khác hoặc chưa rõ ràng
    ELSE N'Khác/ Chưa xác định'
END;











/* 1. TÁCH SỐ TỪ CHUỖI "1 tầng", "2 tầng" */
UPDATE Da_Nang
SET num_floors = CASE 
    -- Nếu là NULL thì đưa về 0
    WHEN num_floors IS NULL THEN '0' 
    -- Nếu có chữ "tầng" hoặc khoảng trắng, lấy phần số ở đầu
    WHEN CHARINDEX(' ', TRIM(CAST(num_floors AS NVARCHAR(MAX)))) > 0 
    THEN LEFT(TRIM(CAST(num_floors AS NVARCHAR(MAX))), CHARINDEX(' ', TRIM(CAST(num_floors AS NVARCHAR(MAX)))) - 1)
    -- Nếu chỉ là số rồi thì giữ nguyên
    ELSE TRIM(CAST(num_floors AS NVARCHAR(MAX))) 
END;

/* 2. ĐƯA CÁC GIÁ TRỊ LỖI (NẾU CÒN) VỀ '0' TRƯỚC KHI CONVERT */
UPDATE Da_Nang
SET num_floors = CASE 
    WHEN ISNUMERIC(num_floors) = 1 THEN num_floors 
    ELSE '0' 
END;

/* 3. CHUYỂN KIỂU DỮ LIỆU SANG INT */
ALTER TABLE Da_Nang ALTER COLUMN num_floors INT;