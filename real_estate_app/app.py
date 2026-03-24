# streamlit run app_v2.py

import streamlit as st
import pandas as pd
import joblib
import folium
from folium.plugins import Geocoder
from streamlit_folium import st_folium
import requests
import re
import plotly.express as px
import os
import numpy as np
from sklearn.neighbors import BallTree

# ---------------------------------------------------------
# CÁC DANH SÁCH CHUẨN CỦA MÔ HÌNH (GỘP THÀNH DICTIONARY ĐỂ DỄ QUẢN LÝ)
# ---------------------------------------------------------
LOCATION_MAPPING = {
    "Hồ Chí Minh":[
        "Quận 6", "Quận 11", "Quận 10", "Quận Bình Thạnh", "Quận 8", "Phường 11", "Quận 1", 
        "Quận Tân Bình", "Quận Phú Nhuận", "Huyện Nhà Bè", "Quận Gò Vấp", "Huyện Hóc Môn", 
        "Quận 7", "Huyện Bình Chánh", "Quận 4", "Quận 12", "Quận 5", "Huyện Cần Giờ", 
        "Quận Tân Phú", "Phường 7", "Thành phố Thủ Đức", "Huyện Củ Chi", "Quận 3", "Quận Bình Tân"
    ],
    "Đà Nẵng":[
        "Quận Thanh Khê", "Quận Cẩm Lệ", "Quận Hải Châu", "Quận Liên Chiểu", 
        "Quận Sơn Trà", "Huyện Hòa Vang", "Quận Ngũ Hành Sơn"
    ],
    "Bình Dương":[
        "Huyện Dầu Tiếng", "Thành phố Thuận An", "Thành phố Dĩ An", "Thành phố Bến Cát", 
        "Huyện Bàu Bàng", "Thành phố Tân Uyên", "Thành phố Thủ Dầu Một", "Huyện Phú Giáo"
    ],
    "Hà Nội":[
        "Huyện Hoài Đức", "Quận Hoàng Mai", "Quận Hoàn Kiếm", "Huyện Ba Vì", "Huyện Thanh Trì", 
        "Quận Ba Đình", "Huyện Chương Mỹ", "Quận Thanh Xuân", "Quận Long Biên", "Quận Nam Từ Liêm", 
        "Huyện Thanh Oai", "Quận Cầu Giấy", "Quận Đống Đa", "Quận Tây Hồ", "Huyện Thường Tín", 
        "Thị xã Sơn Tây", "Huyện Quốc Oai", "Huyện Đan Phượng", "Huyện Đông Anh", "Huyện Thạch Thất", 
        "Huyện Ứng Hòa", "Huyện Gia Lâm", "Huyện Phú Xuyên", "Huyện Mê Linh", "Huyện Phúc Thọ", 
        "Quận Hà Đông", "Quận Bắc Từ Liêm", "Huyện Mỹ Đức", "Quận Hai Bà Trưng", "Huyện Sóc Sơn"
    ]
}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# HÀM HỖ TRỢ XỬ LÝ DỮ LIỆU TỪ BẢN ĐỒ
# ---------------------------------------------------------
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
EARTH_RADIUS_METERS = 6371000

def get_pois_manual(north, south, east, west):
    """
    Gửi yêu cầu trực tiếp tới Overpass API để lấy danh sách các địa điểm tiện ích.
    Giống với file api.py trong thư mục scrape.
    """
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
    
    poi_list = []
    for el in elements:
        poi = {
            'lat': el['lat'] if el['type'] == 'node' else el.get('center', {}).get('lat', 0),
            'lon': el['lon'] if el['type'] == 'node' else el.get('center', {}).get('lon', 0),
            'amenity': el.get('tags', {}).get('amenity'),
            'shop': el.get('tags', {}).get('shop'),
            'leisure': el.get('tags', {}).get('leisure')
        }
        poi_list.append(poi)

    return pd.DataFrame(poi_list)

def calculate_features(target_df, poi_df):
    """
    Tính toán số lượng tiện ích xung quanh các vị trí nhà ở dựa trên bán kính.
    """
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

    if poi_df.empty:
        target_df['num_schools_1km'] = 0
        target_df['num_hospitals_2km'] = 0
        target_df['num_markets_1km'] = 0
        return target_df

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

    return target_df

def get_address_from_coords(lat, lon):
    """Lấy toàn bộ thông tin địa chỉ từ Nominatim (Bắt buộc trả về tiếng Việt)"""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1&accept-language=vi"
    headers = {'User-Agent': 'RealEstateApp/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5).json()
        return response.get('address', {})
    except:
        return {}

def match_location_from_api(address_dict):
    """Hàm khớp chính xác địa chỉ từ API Map với danh sách LOCATION_MAPPING"""
    if not address_dict:
        return "Hồ Chí Minh", "Quận 1" # Fallback mặc định
        
    matched_prov = "Hồ Chí Minh"
    matched_dist = None
    
    api_values =[str(v).lower() for v in address_dict.values()]
    
    for prov in LOCATION_MAPPING.keys():
        prov_lower = prov.lower()
        if any(prov_lower in val for val in api_values):
            matched_prov = prov
            break
            
    dist_list = LOCATION_MAPPING[matched_prov]
    sorted_districts = sorted(dist_list, key=len, reverse=True)
    
    for dist in sorted_districts:
        dist_lower = dist.lower()
        core_name = dist_lower
        for p in["thành phố ", "tỉnh ", "quận ", "huyện ", "thị xã ", "phường "]:
            core_name = core_name.replace(p, "").strip()
        
        for val in api_values:
            val_clean = val.replace(",", "").replace(".", "").strip()
            if dist_lower == val_clean or core_name == val_clean:
                matched_dist = dist
                break
            pattern = r'(?<!\d)' + re.escape(core_name) + r'(?!\d)'
            if re.search(pattern, val_clean):
                matched_dist = dist
                break
                
        if matched_dist: break
        
    if not matched_dist:
        matched_dist = dist_list[0]
        
    return matched_prov, matched_dist

# ---------------------------------------------------------
# CÚP CSS CHO NÚT DỰ ĐOÁN TO HƠN
# ---------------------------------------------------------
def local_css():
    st.markdown("""
        <style>
        /* Tăng kích thước chữ cho các nút trong menu (Radio) */
        div[role="radiogroup"] > label > div:first-of-type {
            zoom: 1.5; /* Phóng to nút gạt (radio dot) */
        }
        div[role="radiogroup"] label p {
            font-size: 24px !important; 
            font-weight: bold !important;
            padding-left: 10px;
        }
        [data-testid="stSidebar"] .stRadio > label {
            font-size: 26px !important;
            font-weight: bold !important;
            color: #FF4B4B;
        }

        /* Tăng kích thước chữ cho các lable của Selectbox, Slider trong menu */
        [data-testid="stSidebar"] .stSelectbox label p, 
        [data-testid="stSidebar"] .stSlider label p {
            font-size: 22px !important;
            font-weight: bold !important;
        }

        /* Tùy chỉnh CSS cho nút dự đoán giá bản lớn */
        .stButton>button {
            height: 4em;
            background-color: #ff4b4b !important;
            color: white !important;
            font-size: 24px !important;
            font-weight: bold;
            border-radius: 10px;
        }
        .stButton>button>div>p {
            font-size: 24px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. CÀI ĐẶT TRANG & THANH ĐIỀU HƯỚNG
# ---------------------------------------------------------
st.set_page_config(page_title="Dự đoán giá BĐS", layout="wide")
local_css()
menu = st.sidebar.radio("Menu",["📊 Tổng quan thị trường", "🤖 Dự đoán giá"])

# ---------------------------------------------------------
# 2. TRANG TỔNG QUAN THỊ TRƯỜNG (EDA)
# ---------------------------------------------------------
if menu == "📊 Tổng quan thị trường":
    st.title("📊 Phân tích dữ liệu Bất Động Sản")
    
    @st.cache_data
    def load_data(): 
        data_path = os.path.join(CURRENT_DIR, "data", "cleaned_data.csv")
        df = pd.read_csv(data_path)
        if 'price_total' in df.columns:
            df['price_billion'] = df['price_total'] / 1e9
        return df
        
    try:
        df = load_data()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Bộ lọc dữ liệu EDA")
        
        prov_list = ["Tất cả"] + list(df['province'].dropna().unique())
        selected_prov = st.sidebar.selectbox("📍 Chọn Tỉnh/Thành phố", prov_list)
        
        cat_list = ["Tất cả"] + list(df['category'].dropna().unique())
        selected_cat = st.sidebar.selectbox("🏠 Chọn Loại BĐS", cat_list)
        
        max_price = float(df['price_billion'].max())
        slider_max = float(df['price_billion'].quantile(0.98)) 
        price_range = st.sidebar.slider(
            "💰 Mức giá (Tỷ VNĐ)", 
            min_value=0.0, 
            max_value=slider_max, 
            value=(0.0, slider_max),
            step=0.5
        )

        filtered_df = df.copy()
        if selected_prov != "Tất cả":
            filtered_df = filtered_df[filtered_df['province'] == selected_prov]
        if selected_cat != "Tất cả":
            filtered_df = filtered_df[filtered_df['category'] == selected_cat]
            
        filtered_df = filtered_df[(filtered_df['price_billion'] >= price_range[0]) & 
                                  (filtered_df['price_billion'] <= price_range[1])]

        if len(filtered_df) == 0:
            st.warning("⚠️ Không có dữ liệu nào phù hợp với bộ lọc hiện tại. Vui lòng điều chỉnh lại!")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng số bài đăng", f"{len(filtered_df):,}")
            col2.metric("Giá trung bình (Tỷ VNĐ)", round(filtered_df['price_billion'].mean(), 2))
            col3.metric("Diện tích trung bình (m2)", round(filtered_df['area'].mean(), 1))
            st.divider()

            st.subheader("📍 Bản đồ phân bổ Bất Động Sản theo Giá trị")
            st.markdown("*(Chấm màu càng đỏ giá càng cao, kích thước chấm thể hiện diện tích)*")
            
            map_df = filtered_df.dropna(subset=['latitude', 'longitude'])
            
            fig_map = px.scatter_mapbox(
                map_df, 
                lat="latitude", 
                lon="longitude", 
                color="price_billion", 
                size="area",           
                color_continuous_scale=px.colors.sequential.YlOrRd, 
                size_max=15, 
                zoom=10 if selected_prov != "Tất cả" else 5, 
                mapbox_style="open-street-map",
                hover_name="district",
                hover_data={"category": True, "price_billion": True, "area": True, "latitude": False, "longitude": False},
                labels={"price_billion": "Giá (Tỷ)", "area": "Diện tích (m2)", "category": "Loại"}
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}) 
            
            st.plotly_chart(fig_map, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})
            
            st.divider()

            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                fig_pie = px.pie(
                    filtered_df, 
                    names='category', 
                    title='Tỷ lệ các loại hình BĐS', 
                    hole=0.4, 
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with chart_col2:
                fig_hist = px.histogram(
                    filtered_df, 
                    x='price_billion', 
                    nbins=40, 
                    title='Phân bố phân khúc giá bán (Tỷ VNĐ)',
                    color_discrete_sequence=['#636EFA'],
                    labels={'price_billion': 'Mức giá (Tỷ VNĐ)'}
                )
                fig_hist.update_layout(yaxis_title="Số lượng bài đăng")
                st.plotly_chart(fig_hist, use_container_width=True)

            chart_col3, chart_col4 = st.columns(2)
            
            with chart_col3:
                if selected_prov != "Tất cả":
                    bar_data = filtered_df.groupby('district')['price_billion'].mean().sort_values(ascending=True).reset_index()
                    title_bar = f'Giá nhà trung bình theo Quận/Huyện ({selected_prov})'
                    y_axis = 'district'
                    y_label = 'Quận / Huyện'
                else:
                    bar_data = filtered_df.groupby('province')['price_billion'].mean().sort_values(ascending=True).reset_index()
                    title_bar = 'Giá nhà trung bình theo Tỉnh/Thành phố'
                    y_axis = 'province'
                    y_label = 'Tỉnh / Thành phố'

                fig_bar = px.bar(
                    bar_data, 
                    x='price_billion', 
                    y=y_axis, 
                    orientation='h', 
                    title=title_bar, 
                    color='price_billion',
                    color_continuous_scale=px.colors.sequential.Blues,
                    labels={'price_billion': 'Giá trung bình (Tỷ VNĐ)', y_axis: y_label}
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with chart_col4:
                fig_scatter = px.scatter(
                    filtered_df, 
                    x='area', 
                    y='price_billion', 
                    color='category', 
                    title='Mối quan hệ giữa Diện tích và Giá tiền',
                    opacity=0.6, 
                    hover_data=['district'],
                    labels={'area': 'Diện tích (m2)', 'price_billion': 'Giá (Tỷ VNĐ)', 'category': 'Loại BĐS'}
                )
                st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Có lỗi xảy ra khi load dữ liệu EDA: {e}")

# ---------------------------------------------------------
# 3. TRANG DỰ ĐOÁN GIÁ (MACHINE LEARNING)
# ---------------------------------------------------------
elif menu == "🤖 Dự đoán giá":
    st.title("🤖 Ứng dụng dự đoán giá nhà bằng AI")

    @st.cache_resource
    def load_pipeline():
        model_path = os.path.join(CURRENT_DIR, "data", "extra_trees_pipeline.joblib")
        return joblib.load(model_path)

    try: pipeline = load_pipeline()
    except:
        st.error("❌ Không tìm thấy file `data/extra_trees_pipeline.joblib`.")
        st.stop()

    if "lat" not in st.session_state:
        st.session_state.lat = 10.938  
        st.session_state.lon = 106.767 
        st.session_state.schools = 1
        st.session_state.markets = 1
        st.session_state.hospitals = 0
        st.session_state.province = "Hồ Chí Minh"
        st.session_state.district = "Quận 1"

    st.markdown("### 📍 Bước 1: Chọn vị trí Bất Động Sản trên bản đồ")
    st.info("💡 Click vào bản đồ: Hệ thống sẽ tự động quét Quận/Huyện, Tỉnh/Thành phố và đếm trường học, siêu thị xung quanh (theo api)!")

    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=13)
    folium.Marker([st.session_state.lat, st.session_state.lon], tooltip="Vị trí đang chọn", icon=folium.Icon(color="red")).add_to(m)
    
    # THÊM THANH TÌM KIẾM (GEOCODER)
    Geocoder().add_to(m)
    
    map_data = st_folium(m, height=400, width=1000)

    # --- XỬ LÝ KHI CLICK VÀO BẢN ĐỒ ---
    if map_data and map_data.get('last_clicked'):
        c_lat = map_data['last_clicked']['lat']
        c_lon = map_data['last_clicked']['lng']
        
        if c_lat != st.session_state.lat or c_lon != st.session_state.lon:
            st.session_state.lat = c_lat
            st.session_state.lon = c_lon
            
            with st.spinner("⏳ Đang phân tích địa chỉ và quét tiện ích xung quanh (sử dụng logic BallTree từ Overpass API)..."):
                # 1. Quét Địa Chỉ
                address_dict = get_address_from_coords(c_lat, c_lon)
                st.session_state.province, st.session_state.district = match_location_from_api(address_dict)
                
                # 2. Xử lý logic giống file api.py
                buffer = 0.02 # Lấy vùng xung quanh vị trí chọn (khỏang 2km)
                north, south = c_lat + buffer, c_lat - buffer
                east, west = c_lon + buffer, c_lon - buffer
                
                pois_df = get_pois_manual(north, south, east, west)
                
                target_df = pd.DataFrame({'latitude': [c_lat], 'longitude': [c_lon]})
                result_df = calculate_features(target_df, pois_df)
                
                if not result_df.empty:
                    st.session_state.schools = int(result_df['num_schools_1km'].iloc[0])
                    st.session_state.markets = int(result_df['num_markets_1km'].iloc[0])
                    st.session_state.hospitals = int(result_df['num_hospitals_2km'].iloc[0])
                else:
                    st.session_state.schools = 0
                    st.session_state.markets = 0
                    st.session_state.hospitals = 0
            
            st.rerun() 

    st.divider()
    st.markdown("### 📝 Bước 2: Nhập các thông tin chi tiết khác")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**1. Hành chính & Pháp lý**")
        
        provinces_list = list(LOCATION_MAPPING.keys())
        current_prov = st.session_state.province if st.session_state.province in provinces_list else "Hồ Chí Minh"
        
        province = st.selectbox("Tỉnh/Thành phố", provinces_list, index=provinces_list.index(current_prov))
        
        if province != st.session_state.province:
            st.session_state.province = province
            st.session_state.district = LOCATION_MAPPING[province][0] 
            st.rerun()
            
        districts_list = LOCATION_MAPPING[st.session_state.province]
        current_dist = st.session_state.district if st.session_state.district in districts_list else districts_list[0]
        
        district = st.selectbox("Quận/Huyện", districts_list, index=districts_list.index(current_dist))
        
        if district != st.session_state.district:
            st.session_state.district = district
        
        category = st.selectbox("Loại BĐS",["Đất nền dự án", "Nhà riêng", "Căn hộ chung cư", "Bán đất", "Nhà mặt phố"])
        legal_status = st.selectbox("Pháp lý",["Sổ đỏ/ Sổ hồng", "Hợp đồng mua bán", "Vi bằng/ Công chứng", "Khác/ Chưa xác định"])
        
    with col2:
        st.markdown("**2. Thông số kỹ thuật**")
        area = st.number_input("Diện tích (m2)", min_value=10.0, max_value=1000.0, value=80.0, step=1.0)
        frontage = st.number_input("Mặt tiền (m)", min_value=0.0, value=5.0, step=0.5)
        road_width = st.number_input("Đường vào (m)", min_value=0.0, value=6.0, step=0.5)
        num_floors = st.number_input("Số tầng", min_value=0, max_value=10, value=1, step=1)
        num_bedrooms = st.number_input("Số phòng ngủ", min_value=0, max_value=20, value=2, step=1)
        num_toilets = st.number_input("Số Toilet", min_value=0, max_value=20, value=2, step=1)
        
    with col3:
        st.markdown("**3. Vị trí & Tiện ích (Auto AI)**")
        st.text_input("Tọa độ Latitude", value=f"{st.session_state.lat:.6f}", disabled=True)
        st.text_input("Tọa độ Longitude", value=f"{st.session_state.lon:.6f}", disabled=True)
        num_schools_1km = st.number_input("Trường học (bán kính 1km)", value=st.session_state.schools, step=1)
        num_markets_1km = st.number_input("Chợ/siêu thị (bán kính 1km)", value=st.session_state.markets, step=1)
        num_hospitals_2km = st.number_input("Bệnh viện (bán kính 2km)", value=st.session_state.hospitals, step=1)

    st.divider()

    st.markdown('<div class="big-btn">', unsafe_allow_html=True)
    if st.button("🚀 BẮT ĐẦU DỰ ĐOÁN GIÁ", type="primary", use_container_width=True):
        input_data = pd.DataFrame({
            'area':[area],
            'category': [category],
            'latitude': [st.session_state.lat], 
            'longitude': [st.session_state.lon],
            'district': [st.session_state.district], 
            'province': [st.session_state.province], 
            'legal_status': [legal_status],
            'frontage': [frontage],
            'road_width': [road_width], 
            'num_bedrooms':[num_bedrooms],
            'num_toilets': [num_toilets],
            'num_floors':[num_floors], 
            'num_schools_1km':[num_schools_1km], 
            'num_hospitals_2km':[num_hospitals_2km],
            'num_markets_1km': [num_markets_1km]
        })

        try:
            prediction_billion = pipeline.predict(input_data)[0]
            prediction_vnd = prediction_billion * 1_000_000_000
            st.success("✨ **KẾT QUẢ DỰ ĐOÁN:**")
            st.markdown(f"<h2 style='text-align: center; color: #FF4B4B;'>{prediction_billion:.2f} Tỷ VNĐ</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>(Tương đương khoảng: {prediction_vnd:,.0f} VNĐ)</p>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"⚠️ Có lỗi xảy ra trong quá trình dự đoán. Chi tiết lỗi: {e}")
    st.markdown('</div>', unsafe_allow_html=True)