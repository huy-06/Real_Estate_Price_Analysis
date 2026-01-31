select distinct district
from Binh_Duong

UPDATE Binh_Duong
SET district = CASE 
    -- Ưu tiên check các từ khóa đặc trưng nhất
    WHEN district LIKE N'%Bắc Tân Uyên%' THEN N'Huyện Bắc Tân Uyên'
    WHEN district LIKE N'%Tân Uyên%'     THEN N'Thành phố Tân Uyên'
    WHEN district LIKE N'%Dĩ An%'        THEN N'Thành phố Dĩ An'
    WHEN district LIKE N'%Thuận An%'     THEN N'Thành phố Thuận An'
    WHEN district LIKE N'%Bến Cát%'      THEN N'Thành phố Bến Cát'
    WHEN district LIKE N'%Thủ Dầu Một%'  THEN N'Thành phố Thủ Dầu Một'
    WHEN district LIKE N'%Bàu Bàng%'     THEN N'Huyện Bàu Bàng'
    WHEN district LIKE N'%Dầu Tiếng%'    THEN N'Huyện Dầu Tiếng'
    WHEN district LIKE N'%Phú Giáo%'     THEN N'Huyện Phú Giáo'
    ELSE district 
END;

UPDATE Ho_Chi_Minh_final
SET district = CASE 
    -- 1. Xử lý Thành phố Thủ Đức (Gồm Thủ Đức cũ, Q2, Q9 và các phường liên quan)
    WHEN district LIKE N'%Thủ Đức%' OR district LIKE N'%Quận 2%' OR district LIKE N'%Quận 9%' 
         OR district LIKE N'%An Khánh%' OR district LIKE N'%Bình Trưng%' THEN N'Thành phố Thủ Đức'

    -- 2. Xử lý các Quận có tên chữ
    WHEN district LIKE N'%Bình Thạnh%' THEN N'Quận Bình Thạnh'
    WHEN district LIKE N'%Gò Vấp%'     THEN N'Quận Gò Vấp'
    WHEN district LIKE N'%Phú Nhuận%'  THEN N'Quận Phú Nhuận'
    WHEN district LIKE N'%Tân Bình%'   THEN N'Quận Tân Bình'
    WHEN district LIKE N'%Tân Phú%'    THEN N'Quận Tân Phú'
    WHEN district LIKE N'%Bình Tân%'   THEN N'Quận Bình Tân'

    -- 3. Xử lý các Huyện
    WHEN district LIKE N'%Hóc Môn%'    THEN N'Huyện Hóc Môn'
    WHEN district LIKE N'%Nhà Bè%'     THEN N'Huyện Nhà Bè'
    WHEN district LIKE N'%Củ Chi%'     THEN N'Huyện Củ Chi'
    WHEN district LIKE N'%Cần Giờ%'    THEN N'Huyện Cần Giờ'
    WHEN district LIKE N'%Bình Chánh%' THEN N'Huyện Bình Chánh'

    -- 4. Xử lý các Quận đánh số (Cần cẩn thận để không nhầm Quận 1 với Quận 10, 11, 12)
    -- Xử lý trường hợp đặc biệt chứa địa chỉ cụ thể như "Bến Bình Đông Quận 8"
    WHEN district LIKE N'%Quận 12%' THEN N'Quận 12'
    WHEN district LIKE N'%Quận 11%' THEN N'Quận 11'
    WHEN district LIKE N'%Quận 10%' THEN N'Quận 10'
    WHEN district LIKE N'%Quận 1%'  AND district NOT LIKE N'%Quận 10%' 
                                    AND district NOT LIKE N'%Quận 11%' 
                                    AND district NOT LIKE N'%Quận 12%' THEN N'Quận 1'
    WHEN district LIKE N'%Quận 3%'  THEN N'Quận 3'
    WHEN district LIKE N'%Quận 4%'  THEN N'Quận 4'
    WHEN district LIKE N'%Quận 5%'  THEN N'Quận 5'
    WHEN district LIKE N'%Quận 6%'  THEN N'Quận 6'
    WHEN district LIKE N'%Quận 7%'  THEN N'Quận 7'
    WHEN district LIKE N'%Quận 8%'  OR district LIKE N'%Bến Bình Đông%' THEN N'Quận 8'

    -- 5. Xử lý các giá trị còn lại (Phường lẻ không rõ Quận hoặc NULL)
    WHEN district IS NULL THEN N'Chưa xác định'
    ELSE district 
END;



UPDATE Ha_Noi
SET district = CASE 
    -- 1. Nhóm 12 Quận (Ưu tiên Nam/Bắc Từ Liêm trước)
    WHEN district LIKE N'%Nam Từ Liêm%' THEN N'Quận Nam Từ Liêm'
    WHEN district LIKE N'%Bắc Từ Liêm%' THEN N'Quận Bắc Từ Liêm'
    WHEN district LIKE N'%Ba Đình%' OR district LIKE N'%Đội Cấn%' OR district LIKE N'%Hồng Hà%' THEN N'Quận Ba Đình'
    WHEN district LIKE N'%Hoàn Kiếm%' THEN N'Quận Hoàn Kiếm'
    WHEN district LIKE N'%Hai Bà Trưng%' THEN N'Quận Hai Bà Trưng'
    WHEN district LIKE N'%Đống Đa%' THEN N'Quận Đống Đa'
    WHEN district LIKE N'%Tây Hồ%' THEN N'Quận Tây Hồ'
    WHEN district LIKE N'%Cầu Giấy%' THEN N'Quận Cầu Giấy'
    WHEN district LIKE N'%Thanh Xuân%' THEN N'Quận Thanh Xuân'
    WHEN district LIKE N'%Hoàng Mai%' THEN N'Quận Hoàng Mai'
    WHEN district LIKE N'%Long Biên%' THEN N'Quận Long Biên'
    WHEN district LIKE N'%Hà Đông%' THEN N'Quận Hà Đông'

    -- 2. Nhóm 1 Thị xã
    WHEN district LIKE N'%Sơn Tây%' THEN N'Thị xã Sơn Tây'

    -- 3. Nhóm 17 Huyện
    WHEN district LIKE N'%Thạch Thất%' OR district LIKE N'%hoà lạc%' THEN N'Huyện Thạch Thất'
    WHEN district LIKE N'%Ba Vì%' THEN N'Huyện Ba Vì'
    WHEN district LIKE N'%Chương Mỹ%' THEN N'Huyện Chương Mỹ'
    WHEN district LIKE N'%Đan Phượng%' THEN N'Huyện Đan Phượng'
    WHEN district LIKE N'%Đông Anh%' THEN N'Huyện Đông Anh'
    WHEN district LIKE N'%Gia Lâm%' THEN N'Huyện Gia Lâm'
    WHEN district LIKE N'%Hoài Đức%' THEN N'Huyện Hoài Đức'
    WHEN district LIKE N'%Mê Linh%' THEN N'Huyện Mê Linh'
    WHEN district LIKE N'%Mỹ Đức%' THEN N'Huyện Mỹ Đức'
    WHEN district LIKE N'%Phú Xuyên%' THEN N'Huyện Phú Xuyên'
    WHEN district LIKE N'%Phúc Thọ%' THEN N'Huyện Phúc Thọ'
    WHEN district LIKE N'%Quốc Oai%' THEN N'Huyện Quốc Oai'
    WHEN district LIKE N'%Sóc Sơn%' THEN N'Huyện Sóc Sơn'
    WHEN district LIKE N'%Thanh Oai%' THEN N'Huyện Thanh Oai'
    WHEN district LIKE N'%Thanh Trì%' THEN N'Huyện Thanh Trì'
    WHEN district LIKE N'%Thường Tín%' THEN N'Huyện Thường Tín'
    WHEN district LIKE N'%Ứng Hòa%' THEN N'Huyện Ứng Hòa'

    -- 4. Trường hợp đặc biệt (Văn Giang thuộc Hưng Yên nhưng hay nằm trong data Hà Nội)
    WHEN district LIKE N'%Văn Giang%' THEN N'Huyện Văn Giang (Hưng Yên)'
    
    -- 5. Xử lý NULL hoặc không xác định
    WHEN district IS NULL THEN N'Chưa xác định'
    ELSE district 
END;



UPDATE Da_Nang
SET district = CASE 
    -- 1. Nhóm các Quận (6 Quận)
    WHEN district LIKE N'%Hải Châu%'    THEN N'Quận Hải Châu'
    WHEN district LIKE N'%Thanh Khê%'   THEN N'Quận Thanh Khê'
    WHEN district LIKE N'%Sơn Trà%'     THEN N'Quận Sơn Trà'
    WHEN district LIKE N'%Ngũ Hành Sơn%' THEN N'Quận Ngũ Hành Sơn'
    WHEN district LIKE N'%Liên Chiểu%'  THEN N'Quận Liên Chiểu'
    WHEN district LIKE N'%Cẩm Lệ%'      THEN N'Quận Cẩm Lệ'

    -- 2. Nhóm các Huyện (2 Huyện)
    WHEN district LIKE N'%Hòa Vang%'    THEN N'Huyện Hòa Vang'
    WHEN district LIKE N'%Hoàng Sa%'    THEN N'Huyện Hoàng Sa'

    -- 3. Xử lý các giá trị khác
    WHEN district IS NULL THEN N'Chưa xác định'
    ELSE district 
END;