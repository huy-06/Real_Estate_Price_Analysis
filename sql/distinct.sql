-- Thay 'Ten_Bang_Cua_Ban' bằng tên bảng thực tế (ví dụ: Binh_Duong)
WITH DanhSachTrung AS (
    SELECT 
        post_id, -- Tên cột bị trùng (Khóa chính)
        post_title, -- Lấy thêm tiêu đề để nhìn cho dễ
        ROW_NUMBER() OVER (
            PARTITION BY post_id       -- Gom nhóm theo cột post_id bị trùng
            ORDER BY (SELECT NULL)     -- Thứ tự sắp xếp (để NULL nghĩa là xóa dòng nào cũng được)
        ) AS SoThuTu
    FROM Da_Nang
)
SELECT * FROM DanhSachTrung WHERE SoThuTu > 1;

WITH DanhSachTrung AS (
    SELECT 
        post_id, 
        ROW_NUMBER() OVER (
            PARTITION BY post_id       -- Quan trọng: Cột bạn muốn check trùng
            ORDER BY (SELECT NULL)     -- Nếu muốn giữ dòng mới nhất, thay (SELECT NULL) bằng (ORDER BY ngay_dang DESC)
        ) AS SoThuTu
    FROM Da_Nang -- <-- Nhớ thay tên bảng của bạn vào đây (ví dụ: Binh_Duong)
)
DELETE FROM DanhSachTrung WHERE SoThuTu > 1;