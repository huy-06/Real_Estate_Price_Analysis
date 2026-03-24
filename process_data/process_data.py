import pandas as pd
import geopandas as gpd

# ---------------------------------------------------------
# 1. ĐỌC DỮ LIỆU GỐC VÀ CHUYỂN THÀNH GEODATAFRAME
# ---------------------------------------------------------
# Giả sử file dữ liệu gốc của bạn tên là 'raw_data.csv' (hoặc bạn có thể dùng thẳng biến df hiện tại của bạn)
df = pd.read_csv("../data/cleaned_data.csv")

# Chuyển DataFrame thành GeoDataFrame để xử lý không gian
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df.longitude, df.latitude),
    crs="EPSG:4326"
)

# Tạo một list để chứa dữ liệu sau khi làm sạch của từng tỉnh
cleaned_gdfs =[]

# ---------------------------------------------------------
# 2. XỬ LÝ ĐÀ NẴNG (Cắt theo GeoJSON)
# ---------------------------------------------------------
gdf_dn = gdf[gdf["province"] == "Đà Nẵng"].copy()
try:
    map_dn = gpd.read_file("../geojson/Đà Nẵng - 63.geojson")
    # Lọc giữ lại các điểm NẰM TRONG ranh giới Đà Nẵng
    gdf_dn_clean = gdf_dn[gdf_dn.geometry.within(map_dn.geometry.unary_union)]
    cleaned_gdfs.append(gdf_dn_clean)
    print(f"Đã làm sạch Đà Nẵng: còn {len(gdf_dn_clean)} BĐS.")
except Exception as e:
    print("Lỗi đọc file GeoJSON Đà Nẵng:", e)
    cleaned_gdfs.append(gdf_dn) # Nếu lỗi thì giữ nguyên data cũ


# ---------------------------------------------------------
# 3. XỬ LÝ HỒ CHÍ MINH (Cắt GeoJSON + Xóa Sân Bay)
# ---------------------------------------------------------
gdf_hcm = gdf[gdf["province"] == "Hồ Chí Minh"].copy()
try:
    map_hcm = gpd.read_file("../geojson/TP. Hồ Chí Minh - 63.geojson")
    
    # 3.1 Cắt các điểm NẰM TRONG ranh giới TP.HCM
    gdf_hcm_clean = gdf_hcm[gdf_hcm.geometry.within(map_hcm.geometry.unary_union)]
    
    # 3.2 Xóa các điểm nằm TRONG SÂN BAY TÂN SƠN NHẤT
    tsn_min_lat, tsn_max_lat = 10.805, 10.828
    tsn_min_lon, tsn_max_lon = 106.645, 106.670
    
    airport_mask = ~((gdf_hcm_clean.geometry.y >= tsn_min_lat) & 
                     (gdf_hcm_clean.geometry.y <= tsn_max_lat) & 
                     (gdf_hcm_clean.geometry.x >= tsn_min_lon) & 
                     (gdf_hcm_clean.geometry.x <= tsn_max_lon))
                     
    gdf_hcm_clean = gdf_hcm_clean[airport_mask]
    cleaned_gdfs.append(gdf_hcm_clean)
    print(f"Đã làm sạch Hồ Chí Minh (gồm cắt mép & xóa sân bay): còn {len(gdf_hcm_clean)} BĐS.")
except Exception as e:
    print("Lỗi đọc file GeoJSON Hồ Chí Minh:", e)
    cleaned_gdfs.append(gdf_hcm)


# ---------------------------------------------------------
# 4. XỬ LÝ BÌNH DƯƠNG (Cắt theo GeoJSON)
# ---------------------------------------------------------
gdf_bd = gdf[gdf["province"] == "Bình Dương"].copy()
try:
    map_bd = gpd.read_file("../geojson/Bình Dương - 63.geojson")
    # Lọc giữ lại các điểm NẰM TRONG ranh giới Bình Dương
    gdf_bd_clean = gdf_bd[gdf_bd.geometry.within(map_bd.geometry.unary_union)]
    cleaned_gdfs.append(gdf_bd_clean)
    print(f"Đã làm sạch Bình Dương: còn {len(gdf_bd_clean)} BĐS.")
except Exception as e:
    print("Lỗi đọc file GeoJSON Bình Dương:", e)
    cleaned_gdfs.append(gdf_bd)


# ---------------------------------------------------------
# 5. GỘP CÁC TỈNH KHÁC (Nếu file raw_data của bạn có các tỉnh khác ngoài 3 tỉnh này)
# ---------------------------------------------------------
other_provinces = gdf[~gdf["province"].isin(["Đà Nẵng", "Hồ Chí Minh", "Bình Dương"])]
if not other_provinces.empty:
    cleaned_gdfs.append(other_provinces)

# ---------------------------------------------------------
# 6. KẾT HỢP DỮ LIỆU VÀ XUẤT RA CSV
# ---------------------------------------------------------
# Gộp tất cả lại thành 1 DataFrame hoàn chỉnh
final_gdf = pd.concat(cleaned_gdfs, ignore_index=True)

# Xóa cột 'geometry' vì file CSV không cần cột tọa độ không gian này
final_df = final_gdf.drop(columns=['geometry'])

final_df["price_billion"] = final_df["price_total"] / 1000000000
final_df = final_df[final_df['area'].between(15, 1000) & final_df['price_billion'].between(0.5, 60)]

# XUẤT FILE 1: cleaned_data.csv (Đầy đủ tất cả các cột)
# Dùng utf-8-sig để file CSV không bị lỗi font tiếng Việt khi mở bằng Excel
final_df.to_csv("../data/cleaned_data.csv", index=False, encoding="utf-8-sig")
print("Đã lưu thành công file: cleaned_data.csv")

# XUẤT FILE 2: train_data.csv (Chỉ lấy các cột cần thiết để train Model)
# ---> LƯU Ý: Bạn thay đổi danh sách các cột trong ngoặc vuông dưới đây cho đúng với nhu cầu nhé!
columns_for_training =[
    'price_total',
	'area',
	'price_per_m2',
	'category',
	'latitude',
	'longitude',
	'district',
	'province',
	'legal_status',
	'frontage', 
	'road_width', 
	'num_bedrooms',
	'num_toilets',
	'num_floors',
	'num_schools_1km', 
	'num_hospitals_2km',
	'num_markets_1km',
	'price_billion'
]

# Kiểm tra xem các cột bạn cần có tồn tại trong DataFrame không để tránh lỗi
existing_train_columns = [col for col in columns_for_training if col in final_df.columns]

train_df = final_df[existing_train_columns]
train_df.to_csv("../data/train_data.csv", index=False, encoding="utf-8-sig")
print("Đã lưu thành công file: train_data.csv")

print("Hoàn tất toàn bộ quá trình làm sạch và xuất file!")