import pandas as pd
import numpy as np

def main():
    print("Đang đọc dữ liệu gốc...")
    # Process from train_data which was the input format expected by advanced_models.py
    # or from cleaned_data.csv. Let's use train_data.csv as the base, because advanced_models.py uses it.
    df = pd.read_csv('../data/train_data.csv')
    df = df.drop_duplicates(keep='first')
    df['price_billion'] = df['price_total'] / 1e9

    print("Chuẩn hóa các cột văn bản...")
    # Chuẩn hóa chuỗi
    categorical_cols = ['category', 'province', 'district', 'legal_status']
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', 'Unknown')
            df[col] = df[col].fillna('Unknown')

    print("Lọc rác và loại bỏ ngoại lai...")
    # Lọc logic: Nhà phải có phòng, đất không cần
    nha_categories = ['Nhà riêng', 'Căn hộ chung cư', 'Nhà mặt phố', 'Nhà biệt thự, liền kề']
    dat_categories = ['Bán đất', 'Đất nền dự án']

    cond_nha = (df['category'].isin(nha_categories)) & (df['num_bedrooms'] > 0) & (df['num_toilets'] > 0)
    cond_dat = df['category'].isin(dat_categories)
    df = df[cond_nha | cond_dat]

    # Lọc giá trị hợp lý theo advanced_models.py
    cond_filter = (
        (df['area'] >= 15) & (df['area'] <= 1000) &
        (df['price_billion'] >= 0.3) & (df['price_billion'] <= 80)
    )
    df = df[cond_filter]

    # IQR filtering trên price_billion theo từng category
    df_parts = []
    for cat in df['category'].unique():
        sub = df[df['category'] == cat].copy()
        Q1 = sub['price_billion'].quantile(0.02)
        Q3 = sub['price_billion'].quantile(0.98)
        sub = sub[(sub['price_billion'] >= Q1) & (sub['price_billion'] <= Q3)]
        df_parts.append(sub)
    df_clean = pd.concat(df_parts, ignore_index=True)
    
    # Save the cleaned dataset before feature engineering as 'cleaned_data_advanced'
    print(f"Lưu cleaned_data_advanced.csv với {df_clean.shape[0]} dòng...")
    df_clean.to_csv('../data/cleaned_data_advanced.csv', index=False, encoding='utf-8-sig')

    print("Thêm các đặc trưng Feature Engineering...")
    # Tạo đặc trưng mới
    df_clean['total_rooms'] = df_clean['num_bedrooms'] + df_clean['num_toilets']
    df_clean['area_per_room'] = df_clean['area'] / (df_clean['total_rooms'] + 1)
    df_clean['area_per_floor'] = df_clean['area'] / (df_clean['num_floors'] + 1)
    df_clean['area_per_bed'] = df_clean['area'] / (df_clean['num_bedrooms'] + 1)
    df_clean['toilet_bed_ratio'] = df_clean['num_toilets'] / (df_clean['num_bedrooms'] + 1)

    # Tiện ích xung quanh
    df_clean['amenity_score'] = (
        df_clean['num_schools_1km'] +
        df_clean['num_hospitals_2km'] +
        df_clean['num_markets_1km']
    )

    # Log area
    df_clean['log_area'] = np.log1p(df_clean['area'])

    # Tương tác giữa diện tích và mặt tiền
    df_clean['area_x_frontage'] = df_clean['area'] * df_clean['frontage'].fillna(0)
    df_clean['frontage_ratio'] = df_clean['frontage'].fillna(0) / (df_clean['area'] + 1)

    # Số phòng trên mỗi tầng
    df_clean['rooms_per_floor'] = df_clean['total_rooms'] / (df_clean['num_floors'] + 1)

    print("Áp dụng Bayesian Target Encoding...")
    train_temp = df_clean.copy()
    train_temp['price_per_m2'] = train_temp['price_total'] / train_temp['area']

    global_median_price_m2 = train_temp['price_per_m2'].median()
    SMOOTHING_WEIGHT = 20

    # Encoding theo (district, category)
    dist_cat_stats = train_temp.groupby(['district', 'category'])['price_per_m2'].agg(['median', 'count'])
    dist_cat_stats['smoothed'] = (
        (dist_cat_stats['count'] * dist_cat_stats['median']) + (SMOOTHING_WEIGHT * global_median_price_m2)
    ) / (dist_cat_stats['count'] + SMOOTHING_WEIGHT)
    dist_cat_dict = dist_cat_stats['smoothed'].to_dict()

    # Encoding theo district
    dist_stats = train_temp.groupby('district')['price_per_m2'].agg(['median', 'count'])
    dist_stats['smoothed'] = (
        (dist_stats['count'] * dist_stats['median']) + (SMOOTHING_WEIGHT * global_median_price_m2)
    ) / (dist_stats['count'] + SMOOTHING_WEIGHT)
    dist_dict = dist_stats['smoothed'].to_dict()

    # Encoding theo province
    prov_stats = train_temp.groupby('province')['price_per_m2'].agg(['median', 'count'])
    prov_stats['smoothed'] = (
        (prov_stats['count'] * prov_stats['median']) + (SMOOTHING_WEIGHT * global_median_price_m2)
    ) / (prov_stats['count'] + SMOOTHING_WEIGHT)
    prov_dict = prov_stats['smoothed'].to_dict()

    df_out = df_clean.copy()

    # Cấp 1: District + Category
    tuples = list(zip(df_out['district'].astype(str), df_out['category'].astype(str)))
    enc1 = pd.Series([dist_cat_dict.get(t, np.nan) for t in tuples], index=df_out.index)

    # Cấp 2: District only
    enc2 = df_out['district'].astype(str).map(dist_dict)

    # Cấp 3: Province only
    enc3 = df_out['province'].astype(str).map(prov_dict)

    # Điền theo thứ tự ưu tiên
    df_out['expected_price_m2'] = enc1.fillna(enc2).fillna(enc3).fillna(global_median_price_m2)
    df_out['expected_price'] = df_out['area'] * df_out['expected_price_m2']
    df_out['log_expected_price'] = np.log1p(df_out['expected_price'])
    df_out.drop(columns=['expected_price_m2'], inplace=True)

    print(f"Lưu train_data_advanced.csv với {df_out.shape[0]} dòng và {df_out.shape[1]} cột...")
    df_out.to_csv('../data/train_data_advanced.csv', index=False, encoding='utf-8-sig')
    
    print("Hoàn tất!")

if __name__ == "__main__":
    main()
