--Bình Dương
update raw_data
set district = case
    when district like N'%Bắc Tân Uyên%' then N'Huyện Bắc Tân Uyên'
    when district like N'%Tân Uyên%'     then N'Thành phố Tân Uyên'
    when district like N'%Dĩ An%'        then N'Thành phố Dĩ An'
    when district like N'%Thuận An%'     then N'Thành phố Thuận An'
    when district like N'%Bến Cát%'      then N'Thành phố Bến Cát'
    when district like N'%Thủ Dầu Một%'  then N'Thành phố Thủ Dầu Một'
    when district like N'%Bàu Bàng%'     then N'Huyện Bàu Bàng'
    when district like N'%Dầu Tiếng%'    then N'Huyện Dầu Tiếng'
    when district like N'%Phú Giáo%'     then N'Huyện Phú Giáo'
    else district 
end;

--Thành phố Hồ Chí Minh
update raw_data
set district = case
    when district like N'%Thủ Đức%' or district like N'%Quận 2%' or district like N'%Quận 9%' 
         or district like N'%An Khánh%' or district like N'%Bình Trưng%' then N'Thành phố Thủ Đức'

    when district like N'%Bình Thạnh%' then N'Quận Bình Thạnh'
    when district like N'%Gò Vấp%'     then N'Quận Gò Vấp'
    when district like N'%Phú Nhuận%'  then N'Quận Phú Nhuận'
    when district like N'%Tân Bình%'   then N'Quận Tân Bình'
    when district like N'%Tân Phú%'    then N'Quận Tân Phú'
    when district like N'%Bình Tân%'   then N'Quận Bình Tân'

    when district like N'%Hóc Môn%'    then N'Huyện Hóc Môn'
    when district like N'%Nhà Bè%'     then N'Huyện Nhà Bè'
    when district like N'%Củ Chi%'     then N'Huyện Củ Chi'
    when district like N'%Cần Giờ%'    then N'Huyện Cần Giờ'
    when district like N'%Bình Chánh%' then N'Huyện Bình Chánh'

    when district like N'%Quận 12%' then N'Quận 12'
    when district like N'%Quận 11%' then N'Quận 11'
    when district like N'%Quận 10%' then N'Quận 10'
    when district like N'%Quận 1%'  and district not like N'%Quận 10%' 
                                    and district not like N'%Quận 11%' 
                                    and district not like N'%Quận 12%' then N'Quận 1'
    when district like N'%Quận 3%'  then N'Quận 3'
    when district like N'%Quận 4%'  then N'Quận 4'
    when district like N'%Quận 5%'  then N'Quận 5'
    when district like N'%Quận 6%'  then N'Quận 6'
    when district like N'%Quận 7%'  then N'Quận 7'
    when district like N'%Quận 8%'  or district like N'%Bến Bình Đông%' then N'Quận 8'

    when district is null then N'Chưa xác định'
    else district 
end;


--Hà Nội
update raw_data
set district = case
    when district like N'%Nam Từ Liêm%' then N'Quận Nam Từ Liêm'
    when district like N'%Bắc Từ Liêm%' then N'Quận Bắc Từ Liêm'
    when district like N'%Ba Đình%' or district like N'%Đội Cấn%' or district like N'%Hồng Hà%' then N'Quận Ba Đình'
    when district like N'%Hoàn Kiếm%' then N'Quận Hoàn Kiếm'
    when district like N'%Hai Bà Trưng%' then N'Quận Hai Bà Trưng'
    when district like N'%Đống Đa%' then N'Quận Đống Đa'
    when district like N'%Tây Hồ%' then N'Quận Tây Hồ'
    when district like N'%Cầu Giấy%' then N'Quận Cầu Giấy'
    when district like N'%Thanh Xuân%' then N'Quận Thanh Xuân'
    when district like N'%Hoàng Mai%' then N'Quận Hoàng Mai'
    when district like N'%Long Biên%' then N'Quận Long Biên'
    when district like N'%Hà Đông%' then N'Quận Hà Đông'

    when district like N'%Sơn Tây%' then N'Thị xã Sơn Tây'

    when district like N'%Thạch Thất%' or district like N'%hoà lạc%' then N'Huyện Thạch Thất'
    when district like N'%Ba Vì%' then N'Huyện Ba Vì'
    when district like N'%Chương Mỹ%' then N'Huyện Chương Mỹ'
    when district like N'%Đan Phượng%' then N'Huyện Đan Phượng'
    when district like N'%Đông Anh%' then N'Huyện Đông Anh'
    when district like N'%Gia Lâm%' then N'Huyện Gia Lâm'
    when district like N'%Hoài Đức%' then N'Huyện Hoài Đức'
    when district like N'%Mê Linh%' then N'Huyện Mê Linh'
    when district like N'%Mỹ Đức%' then N'Huyện Mỹ Đức'
    when district like N'%Phú Xuyên%' then N'Huyện Phú Xuyên'
    when district like N'%Phúc Thọ%' then N'Huyện Phúc Thọ'
    when district like N'%Quốc Oai%' then N'Huyện Quốc Oai'
    when district like N'%Sóc Sơn%' then N'Huyện Sóc Sơn'
    when district like N'%Thanh Oai%' then N'Huyện Thanh Oai'
    when district like N'%Thanh Trì%' then N'Huyện Thanh Trì'
    when district like N'%Thường Tín%' then N'Huyện Thường Tín'
    when district like N'%Ứng Hòa%' then N'Huyện Ứng Hòa'

    when district like N'%Văn Giang%' then N'Huyện Văn Giang (Hưng Yên)'
    
    when district is null then N'Chưa xác định'
    else district 
end;

--Đà Nẵng
update raw_data
set district = case
    when district like N'%Hải Châu%'    then N'Quận Hải Châu'
    when district like N'%Thanh Khê%'   then N'Quận Thanh Khê'
    when district like N'%Sơn Trà%'     then N'Quận Sơn Trà'
    when district like N'%Ngũ Hành Sơn%' then N'Quận Ngũ Hành Sơn'
    when district like N'%Liên Chiểu%'  then N'Quận Liên Chiểu'
    when district like N'%Cẩm Lệ%'      then N'Quận Cẩm Lệ'

    when district like N'%Hòa Vang%'    then N'Huyện Hòa Vang'
    when district like N'%Hoàng Sa%'    then N'Huyện Hoàng Sa'

    when district is null then N'Chưa xác định'
    else district 
end;