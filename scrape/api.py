import pandas as pd
import numpy as np
import osmnx as ox
from sklearn.neighbors import BallTree
import os
import requests
import json

# ==============================================================================
# CẤU HÌNH CHO ĐÀ NẴNG
# ==============================================================================
# Kiểm tra lại đường dẫn file này của bạn nhé
FILE_PATH = r"E:\Study\FPT\S3\ADY201m\my\new\raw_data\Da_Nang.csv"

# ==============================================================================
# HÀM TẢI DỮ LIỆU THỦ CÔNG (BYPASS BUG OSMNX)
# ==============================================================================
def get_pois_manual(north, south, east, west):
    print(f"-> Đang gửi yêu cầu trực tiếp tới Overpass API cho khu vực ĐÀ NẴNG...")
    
    query = f"""
    [out:json][timeout:600];
    (
      node["amenity"~"school|kindergarten|university|hospital|clinic|pharmacy|marketplace|cafe|restaurant|bank|atm"]({south},{west},{north},{east});
      way["amenity"~"school|kindergarten|university|hospital|clinic|pharmacy|marketplace|cafe|restaurant|bank|atm"]({south},{west},{north},{east});
      node["shop"~"supermarket|convenience|mall"]({south},{west},{north},{east});
      way["shop"~"supermarket|convenience|mall"]({south},{west},{north},{east});
      node["leisure"="park"]({south},{west},{north},{east});
      way["leisure"="park"]({south},{west},{north},{east});
    );
    out center;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}, timeout=600)
        data = response.json()
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

    elements = data.get('elements', [])
    print(f"-> Đã nhận được {len(elements)} địa điểm tiện ích tại Đà Nẵng.")

    poi_list = []
    for el in elements:
        poi = {}
        if el['type'] == 'node':
            poi['lat'] = el['lat']
            poi['lon'] = el['lon']
        else:
            poi['lat'] = el['center']['lat']
            poi['lon'] = el['center']['lon']
        
        tags = el.get('tags', {})
        poi['amenity'] = tags.get('amenity')
        poi['shop'] = tags.get('shop')
        poi['leisure'] = tags.get('leisure')
        
        poi_list.append(poi)
    
    return pd.DataFrame(poi_list)

# ==============================================================================
# CHƯƠNG TRÌNH CHÍNH
# ==============================================================================
if __name__ == "__main__":
    if not os.path.exists(FILE_PATH):
        print(f"LỖI: Không tìm thấy file tại {FILE_PATH}")
        exit()

    # 1. Đọc dữ liệu
    df = pd.read_csv(FILE_PATH)
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # --- THIẾT LẬP VÙNG LỌC TỌA ĐỘ ĐÀ NẴNG ---
    # Vĩ độ Đà Nẵng: ~15.9 đến 16.2
    # Kinh độ Đà Nẵng: ~107.8 đến 108.4
    initial_len = len(df)
    df = df[(df['latitude'] > 15.5) & (df['latitude'] < 16.5) & 
            (df['longitude'] > 107.5) & (df['longitude'] < 108.6)]
    
    print(f"-> Đã lọc {initial_len - len(df)} dòng tọa độ không thuộc vùng Đà Nẵng.")
    print(f"-> Số lượng dòng nhà ở Đà Nẵng cần xử lý: {len(df)}")

    if df.empty:
        print("CẢNH BÁO: Không có dữ liệu nhà ở hợp lệ trong vùng Đà Nẵng.")
        exit()

    # 2. Xác định vùng BBox tự động
    buffer = 0.015 
    north, south = df['latitude'].max() + buffer, df['latitude'].min() - buffer
    east, west = df['longitude'].max() + buffer, df['longitude'].min() - buffer

    # 3. Tải dữ liệu tiện ích
    pois_df = get_pois_manual(north, south, east, west)

    if pois_df is None or pois_df.empty:
        print("LỖI: Không lấy được dữ liệu tiện ích.")
        exit()

    # 4. Tính toán số lượng tiện ích
    def calculate_features(target_df, poi_df):
        print("--- Đang tính toán khoảng cách tiện ích tại ĐÀ NẴNG ---")
        
        house_coords = np.radians(target_df[['latitude', 'longitude']].values)
        earth_radius = 6371000

        def get_count(subset, radius_m):
            if subset.empty: return 0
            poi_coords = np.radians(subset[['lat', 'lon']].values)
            tree = BallTree(poi_coords, metric='haversine')
            return tree.query_radius(house_coords, r=radius_m/earth_radius, count_only=True)

        target_df['num_schools_1km'] = get_count(poi_df[poi_df['amenity'].isin(['school', 'kindergarten', 'university'])], 1000)
        target_df['num_hospitals_2km'] = get_count(poi_df[poi_df['amenity'].isin(['hospital', 'clinic'])], 2000)
        
        mkt_tags = ['supermarket', 'mall', 'convenience']
        target_df['num_markets_1km'] = get_count(poi_df[(poi_df['shop'].isin(mkt_tags)) | (poi_df['amenity'] == 'marketplace')], 1000)
        
        target_df['num_food_500m'] = get_count(poi_df[poi_df['amenity'].isin(['cafe', 'restaurant'])], 500)
        target_df['num_parks_2km'] = get_count(poi_df[poi_df['leisure'] == 'park'], 2000)
        target_df['num_banks_500m'] = get_count(poi_df[poi_df['amenity'].isin(['bank', 'atm'])], 500)

        return target_df

    # 5. Lưu kết quả
    df = calculate_features(df, pois_df)
    
    final_path = FILE_PATH.replace(".csv", "_final.csv")
    df.to_csv(final_path, index=False, encoding='utf-8-sig')
    
    print(f"\n--- HOÀN TẤT ĐÀ NẴNG ---")
    print(f"Kết quả đã được lưu tại: {final_path}")