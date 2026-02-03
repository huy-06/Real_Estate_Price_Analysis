--Lọc dữ liệu duy nhất rồi lưu vào bảng temp
select distinct 
	*
into 
	temp
from 
	raw_data

--Xóa bảng raw_data
delete from 
	raw_data

--Chèn lại dừ liệu từ bảng temp vào raw_data
insert into
	raw_data
select 
	*
from	
	temp

--Xóa bảng temp
drop table
	temp