"""
Module hỗ trợ tải dữ liệu tiện ích (POI) từ Overpass API và tính toán các đặc trưng
vị trí cho dữ liệu bất động sản tại khu vực Đà Nẵng.
"""

import json
import os
import requests

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

# Cấu hình hằng số
FILE_PATH = r"E:\Study\FPT\S3\ADY201m\my\new\raw_data\Da_Nang.csv"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
EARTH_RADIUS_METERS = 6371000


def get_pois_manual(north, south, east, west):
    """
    Gửi yêu cầu trực tiếp tới Overpass API để lấy danh sách các địa điểm tiện ích.

    Args:
        north (float): Vĩ độ phía Bắc.
        south (float): Vĩ độ phía Nam.
        east (float): Kinh độ phía Đông.
        west (float): Kinh độ phía Tây.

    Returns:
        pd.DataFrame: Danh sách các POI với tọa độ và thông tin loại hình.
    """
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

    try:
        response = requests.post(OVERPASS_URL, data={'data': query}, timeout=600)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return pd.DataFrame()

    elements = data.get('elements', [])
    print(f"-> Đã nhận được {len(elements)} địa điểm tiện ích tại Đà Nẵng.")

    poi_list = []
    for el in elements:
        poi = {
            'lat': el['lat'] if el['type'] == 'node' else el['center']['lat'],
            'lon': el['lon'] if el['type'] == 'node' else el['center']['lon'],
            'amenity': el.get('tags', {}).get('amenity'),
            'shop': el.get('tags', {}).get('shop'),
            'leisure': el.get('tags', {}).get('leisure')
        }
        poi_list.append(poi)

    return pd.DataFrame(poi_list)


def calculate_features(target_df, poi_df):
    """
    Tính toán số lượng tiện ích xung quanh các vị trí nhà ở dựa trên bán kính.

    Args:
        target_df (pd.DataFrame): DataFrame chứa tọa độ nhà ở.
        poi_df (pd.DataFrame): DataFrame chứa tọa độ các tiện ích.

    Returns:
        pd.DataFrame: DataFrame đã được bổ sung các cột đặc trưng mới.
    """
    print("--- Đang tính toán khoảng cách tiện ích tại ĐÀ NẴNG ---")

    house_coords = np.radians(target_df[['latitude', 'longitude']].values)

    def get_count(subset, radius_m):
        if subset.empty:
            return np.zeros(len(target_df), dtype=int)
        
        poi_coords = np.radians(subset[['lat', 'lon']].values)
        tree = BallTree(poi_coords, metric='haversine')
        return tree.query_radius(
            house_coords, 
            r=radius_m / EARTH_RADIUS_METERS, 
            count_only=True
        )

    # Tính toán từng nhóm tiện ích
    target_df['num_schools_1km'] = get_count(
        poi_df[poi_df['amenity'].isin(['school', 'kindergarten', 'university'])], 1000
    )
    target_df['num_hospitals_2km'] = get_count(
        poi_df[poi_df['amenity'].isin(['hospital', 'clinic'])], 2000
    )
    
    mkt_tags = ['supermarket', 'mall', 'convenience']
    target_df['num_markets_1km'] = get_count(
        poi_df[(poi_df['shop'].isin(mkt_tags)) | (poi_df['amenity'] == 'marketplace')], 1000
    )
    
    target_df['num_food_500m'] = get_count(
        poi_df[poi_df['amenity'].isin(['cafe', 'restaurant'])], 500
    )
    target_df['num_parks_2km'] = get_count(
        poi_df[poi_df['leisure'] == 'park'], 2000
    )
    target_df['num_banks_500m'] = get_count(
        poi_df[poi_df['amenity'].isin(['bank', 'atm'])], 500
    )

    return target_df


def main():
    """Luồng thực thi chính của chương trình."""
    if not os.path.exists(FILE_PATH):
        print(f"LỖI: Không tìm thấy file tại {FILE_PATH}")
        return

    # 1. Đọc và làm sạch dữ liệu
    df = pd.read_csv(FILE_PATH)
    df = df.dropna(subset=['latitude', 'longitude'])
    
    # Lọc tọa độ trong vùng Đà Nẵng
    initial_len = len(df)
    df = df[
        (df['latitude'] > 15.5) & (df['latitude'] < 16.5) & 
        (df['longitude'] > 107.5) & (df['longitude'] < 108.6)
    ]
    
    print(f"-> Đã lọc {initial_len - len(df)} dòng tọa độ không thuộc Đà Nẵng.")
    print(f"-> Số lượng dòng cần xử lý: {len(df)}")

    if df.empty:
        print("CẢNH BÁO: Không có dữ liệu hợp lệ.")
        return

    # 2. Xác định vùng BBox tự động (có buffer)
    buffer = 0.015 
    north, south = df['latitude'].max() + buffer, df['latitude'].min() - buffer
    east, west = df['longitude'].max() + buffer, df['longitude'].min() - buffer

    # 3. Tải dữ liệu tiện ích
    pois_df = get_pois_manual(north, south, east, west)

    if pois_df.empty:
        print("LỖI: Không lấy được dữ liệu tiện ích.")
        return

    # 4. Tính toán đặc trưng và lưu kết quả
    df = calculate_features(df, pois_df)
    
    final_path = FILE_PATH.replace(".csv", "_final.csv")
    df.to_csv(final_path, index=False, encoding='utf-8-sig')
    
    print(f"\n--- HOÀN TẤT ĐÀ NẴNG ---")
    print(f"Kết quả đã được lưu tại: {final_path}")


if __name__ == "__main__":
    main()