import pandas as pd
import os

def main():
    print("Đang đọc dữ liệu đầu vào...")
    input_file = '../data/train_data.csv'
    output_file = '../data/filtered_data.csv'
    
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file {input_file}")
        return
        
    df = pd.read_csv(input_file)
    print(f"Dữ liệu gốc có {df.shape[0]} dòng và {df.shape[1]} cột.")
    
    # Các cột cần thiết cho advanced_models.py và dashboard app
    columns_to_keep = [
        'price_total', 'area', 'category', 'latitude', 'longitude', 
        'district', 'province', 'legal_status', 'frontage', 'road_width', 
        'num_bedrooms', 'num_toilets', 'num_floors', 'num_schools_1km', 
        'num_hospitals_2km', 'num_markets_1km'
    ]
    
    # Lọc ra các cột có tồn tại trong dataframe
    valid_cols = [col for col in columns_to_keep if col in df.columns]
    
    df_filtered = df[valid_cols]
    
    # Lưu ra file mới
    df_filtered.to_csv(output_file, index=False)
    print(f"Đã lưu dữ liệu đã lọc ra {output_file}.")
    print(f"Dữ liệu mới có {df_filtered.shape[0]} dòng và {df_filtered.shape[1]} cột.")

if __name__ == "__main__":
    main()
