--Dọn dẹp ký tự lạ và chuẩn hóa số liệu (area, frontage, road_width)
update raw_data
set 
    area = replace(replace(replace(lower(cast(area as nvarchar(max))), 'm2', ''), ',', '.'), ' ', ''),
    frontage = replace(replace(replace(lower(cast(frontage as nvarchar(max))), 'm', ''), ',', '.'), ' ', ''),
    road_width = replace(replace(replace(lower(cast(road_width as nvarchar(max))), 'm', ''), ',', '.'), ' ', '');

--Xử lý số phòng ngủ và số toilet (lấy ký tự số đầu tiên)
update raw_data
set 
    num_bedrooms = case 
        when isnumeric(left(trim(cast(num_bedrooms as nvarchar(max))), 1)) = 1 
        then left(trim(cast(num_bedrooms as nvarchar(max))), 1) 
        else '0' end,
    num_toilets = case 
        when isnumeric(left(trim(cast(num_toilets as nvarchar(max))), 1)) = 1 
        then left(trim(cast(num_toilets as nvarchar(max))), 1) 
        else '0' end;

--Đưa các giá trị không phải số về null để chuẩn bị ép kiểu
update raw_data
set 
    area = case when isnumeric(area) = 1 then area else null end,
    frontage = case when isnumeric(frontage) = 1 then frontage else null end,
    road_width = case when isnumeric(road_width) = 1 then road_width else null end,
    price_total = case when isnumeric(price_total) = 1 then price_total else null end;

--Xử lý giá trị null và thay đổi kiểu dữ liệu cột sang số
update raw_data set area = 0 where area is null;
update raw_data set price_total = 0 where price_total is null;
update raw_data set num_bedrooms = 0 where num_bedrooms is null;
update raw_data set num_toilets = 0 where num_toilets is null;
update raw_data set frontage = 0 where frontage is null;
update raw_data set road_width = 0 where road_width is null;

alter table raw_data alter column area float;
alter table raw_data alter column price_total bigint;
alter table raw_data alter column num_bedrooms int;
alter table raw_data alter column num_toilets int;
alter table raw_data alter column frontage float;
alter table raw_data alter column road_width float;

--Loại bỏ các dòng không có giá bán
delete from raw_data where price_total <= 0;

--Chuẩn hóa danh mục và phân nhóm pháp lý (legal_status)
update raw_data set category = trim(category);

update raw_data
set legal_status = case 
    when legal_status like n'%sổ đỏ%' 
      or legal_status like n'%sổ hồng%' 
      or legal_status like n'%sổ riêng%' 
      or legal_status like n'%sổ sẵn%' 
      or legal_status like n'%sổ hoàn công%'
      or legal_status like n'%Sổ chung%' 
      or legal_status like n'%đã có sổ%' 
      or legal_status like n'%Có sổ%' then n'Sổ đỏ/ Sổ hồng'
    when legal_status like n'%HĐMB%' 
      or legal_status like n'%Hợp đồng%' 
      or legal_status like n'%Văn bản%' 
      or legal_status like n'%VBTT%' 
      or legal_status like n'%đang chờ%' then n'Hợp đồng mua bán'
    when legal_status like n'%vi bằng%' 
      or legal_status like n'%Công chứng%' then n'Vi bằng/ Công chứng'
    else n'Khác/ Chưa xác định'
end;

--Xử lý số tầng (num_floors)
update raw_data
set num_floors = case 
    when num_floors is null then '0' 
    when charindex(' ', trim(cast(num_floors as nvarchar(max)))) > 0 
    then left(trim(cast(num_floors as nvarchar(max))), charindex(' ', trim(cast(num_floors as nvarchar(max)))) - 1)
    else trim(cast(num_floors as nvarchar(max))) 
end;

update raw_data
set num_floors = case 
    when isnumeric(num_floors) = 1 then num_floors 
    else '0' 
end;