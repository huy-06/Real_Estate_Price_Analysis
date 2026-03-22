# streamlit run app.py

import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import requests
import re
import plotly.express as px
import os

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
def get_poi_count(lat, lon, radius, tags):
    """Đếm tiện ích xung quanh tọa độ"""
    overpass_url = "http://overpass-api.de/api/interpreter"
    query_parts =[]
    for k, v in tags:
        query_parts.append(f'node["{k}"="{v}"](around:{radius},{lat},{lon});')
        query_parts.append(f'way["{k}"="{v}"](around:{radius},{lat},{lon});')
    query = f"[out:json];({''.join(query_parts)});out count;"
    try:
        response = requests.get(overpass_url, params={'data': query}, timeout=10).json()
        return int(response['elements'][0]['tags']['total'])
    except:
        return 0

def get_address_from_coords(lat, lon):
    """Lấy toàn bộ thông tin địa chỉ từ Nominatim (Bắt buộc trả về tiếng Việt)"""
    # Thêm tham số &accept-language=vi để tránh lỗi API trả về tiếng Anh (Ho Chi Minh City)
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
    
    # Gom tất cả các values API trả về thành chữ thường
    api_values =[str(v).lower() for v in address_dict.values()]
    
    # 1. TÌM TỈNH / THÀNH PHỐ
    for prov in LOCATION_MAPPING.keys():
        prov_lower = prov.lower()
        if any(prov_lower in val for val in api_values):
            matched_prov = prov
            break
            
    # 2. TÌM QUẬN / HUYỆN (Chỉ dò trong Tỉnh đã tìm thấy)
    dist_list = LOCATION_MAPPING[matched_prov]
    
    # Ưu tiên dò chữ dài trước (tránh dò Quận 1 trước Quận 10)
    sorted_districts = sorted(dist_list, key=len, reverse=True)
    
    for dist in sorted_districts:
        dist_lower = dist.lower()
        
        # Bỏ tiền tố để lấy lõi (VD: "Thành phố Dĩ An" -> "dĩ an")
        core_name = dist_lower
        for p in["thành phố ", "tỉnh ", "quận ", "huyện ", "thị xã ", "phường "]:
            core_name = core_name.replace(p, "").strip()
        
        for val in api_values:
            val_clean = val.replace(",", "").replace(".", "").strip()
            
            # Khớp tuyệt đối (VD: "quận 1")
            if dist_lower == val_clean or core_name == val_clean:
                matched_dist = dist
                break
            
            # Khớp bằng Regex để phân biệt ranh giới từ (Tránh lỗi 1 nhầm thành 10, 11)
            pattern = r'(?<!\d)' + re.escape(core_name) + r'(?!\d)'
            if re.search(pattern, val_clean):
                matched_dist = dist
                break
                
        if matched_dist: break
        
    # Nếu dò mãi không ra thì lấy quận đầu tiên của Tỉnh đó làm mặc định
    if not matched_dist:
        matched_dist = dist_list[0]
        
    return matched_prov, matched_dist

# ---------------------------------------------------------
# 1. CÀI ĐẶT TRANG & THANH ĐIỀU HƯỚNG
# ---------------------------------------------------------
st.set_page_config(page_title="Dự đoán giá BĐS", layout="wide")
menu = st.sidebar.radio("Menu",["📊 Tổng quan thị trường", "🤖 Dự đoán giá"])

# ---------------------------------------------------------
# 2. TRANG TỔNG QUAN THỊ TRƯỜNG (EDA)
# ---------------------------------------------------------
if menu == "📊 Tổng quan thị trường":
    st.title("📊 Phân tích dữ liệu Bất Động Sản")
    
    @st.cache_data
    def load_data(): 
        # Tải dữ liệu và tạo thêm cột giá trị theo Tỷ VNĐ để dễ xem
        data_path = os.path.join(CURRENT_DIR, "data", "cleaned_data.csv")
        df = pd.read_csv(data_path)

        if 'price_total' in df.columns:
            df['price_billion'] = df['price_total'] / 1e9
        return df
        
    try:
        df = load_data()
        
        # --- BỘ LỌC DỮ LIỆU (SIDEBAR) ---
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Bộ lọc dữ liệu EDA")
        
        # Lọc theo Tỉnh/Thành phố
        prov_list = ["Tất cả"] + list(df['province'].dropna().unique())
        selected_prov = st.sidebar.selectbox("📍 Chọn Tỉnh/Thành phố", prov_list)
        
        # Lọc theo Loại BĐS
        cat_list = ["Tất cả"] + list(df['category'].dropna().unique())
        selected_cat = st.sidebar.selectbox("🏠 Chọn Loại BĐS", cat_list)
        
        # Lọc theo Khoảng giá (Tỷ VNĐ)
        max_price = float(df['price_billion'].max())
        # Cắt mức giá ở percentile 98 để thanh trượt không bị dãn quá mức bởi các outlier (nhà siêu đắt)
        slider_max = float(df['price_billion'].quantile(0.98)) 
        price_range = st.sidebar.slider(
            "💰 Mức giá (Tỷ VNĐ)", 
            min_value=0.0, 
            max_value=slider_max, 
            value=(0.0, slider_max),
            step=0.5
        )

        # --- ÁP DỤNG BỘ LỌC VÀO DATAFRAME ---
        filtered_df = df.copy()
        if selected_prov != "Tất cả":
            filtered_df = filtered_df[filtered_df['province'] == selected_prov]
        if selected_cat != "Tất cả":
            filtered_df = filtered_df[filtered_df['category'] == selected_cat]
            
        filtered_df = filtered_df[(filtered_df['price_billion'] >= price_range[0]) & 
                                  (filtered_df['price_billion'] <= price_range[1])]

        # Kiểm tra nếu bộ lọc không có dữ liệu
        if len(filtered_df) == 0:
            st.warning("⚠️ Không có dữ liệu nào phù hợp với bộ lọc hiện tại. Vui lòng điều chỉnh lại!")
        else:
            # --- CÁC CHỈ SỐ TỔNG QUAN (METRICS) ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng số bài đăng", f"{len(filtered_df):,}")
            col2.metric("Giá trung bình (Tỷ VNĐ)", round(filtered_df['price_billion'].mean(), 2))
            col3.metric("Diện tích trung bình (m2)", round(filtered_df['area'].mean(), 1))
            st.divider()

            # --- BẢN ĐỒ TƯƠNG TÁC (CHẤM MÀU THEO GIÁ) ---
            st.subheader("📍 Bản đồ phân bổ Bất Động Sản theo Giá trị")
            st.markdown("*(Chấm màu càng đỏ giá càng cao, kích thước chấm thể hiện diện tích)*")
            
            # Xóa các dòng thiếu tọa độ để vẽ bản đồ không bị lỗi
            map_df = filtered_df.dropna(subset=['latitude', 'longitude'])
            
            fig_map = px.scatter_mapbox(
                map_df, 
                lat="latitude", 
                lon="longitude", 
                color="price_billion", # Màu sắc theo giá
                size="area",           # Kích thước theo diện tích
                color_continuous_scale=px.colors.sequential.YlOrRd, # Thang màu Vàng -> Đỏ
                size_max=15, 
                zoom=10 if selected_prov != "Tất cả" else 5, 
                mapbox_style="open-street-map",
                hover_name="district",
                hover_data={"category": True, "price_billion": True, "area": True, "latitude": False, "longitude": False},
                labels={"price_billion": "Giá (Tỷ)", "area": "Diện tích (m2)", "category": "Loại"}
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}) # Bỏ viền thừa của bản đồ
            
            # THÊM config={'scrollZoom': True} ĐỂ CHO PHÉP ZOOM BẰNG CON LĂN CHUỘT
            st.plotly_chart(fig_map, width="stretch", config={'scrollZoom': True, 'displayModeBar': True})
            
            st.divider()

            # --- VẼ BIỂU ĐỒ TỔNG QUAN ---
            # Hàng 1: Tỷ lệ loại hình & Phân bố giá
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Biểu đồ Donut Chart (Tỷ lệ loại BĐS)
                fig_pie = px.pie(
                    filtered_df, 
                    names='category', 
                    title='Tỷ lệ các loại hình BĐS', 
                    hole=0.4, # Tạo lỗ ở giữa (Donut chart)
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, width="stretch")
                
            with chart_col2:
                # Biểu đồ Histogram (Phân bố mức giá)
                fig_hist = px.histogram(
                    filtered_df, 
                    x='price_billion', 
                    nbins=40, 
                    title='Phân bố phân khúc giá bán (Tỷ VNĐ)',
                    color_discrete_sequence=['#636EFA'],
                    labels={'price_billion': 'Mức giá (Tỷ VNĐ)'}
                )
                fig_hist.update_layout(yaxis_title="Số lượng bài đăng")
                st.plotly_chart(fig_hist, width="stretch")

            # Hàng 2: So sánh giá theo khu vực & Scatter Plot
            chart_col3, chart_col4 = st.columns(2)
            
            with chart_col3:
                # Biểu đồ cột so sánh giá khu vực
                if selected_prov != "Tất cả":
                    # Nếu đã chọn Tỉnh, so sánh giá giữa các Quận/Huyện của Tỉnh đó
                    bar_data = filtered_df.groupby('district')['price_billion'].mean().sort_values(ascending=True).reset_index()
                    title_bar = f'Giá nhà trung bình theo Quận/Huyện ({selected_prov})'
                    y_axis = 'district'
                    y_label = 'Quận / Huyện'
                else:
                    # Nếu chọn "Tất cả", so sánh giá giữa các Tỉnh/Thành phố
                    bar_data = filtered_df.groupby('province')['price_billion'].mean().sort_values(ascending=True).reset_index()
                    title_bar = 'Giá nhà trung bình theo Tỉnh/Thành phố'
                    y_axis = 'province'
                    y_label = 'Tỉnh / Thành phố'

                fig_bar = px.bar(
                    bar_data, 
                    x='price_billion', 
                    y=y_axis, 
                    orientation='h', # Cột nằm ngang cho dễ đọc tên dài
                    title=title_bar, 
                    color='price_billion',
                    color_continuous_scale=px.colors.sequential.Blues,
                    labels={'price_billion': 'Giá trung bình (Tỷ VNĐ)', y_axis: y_label}
                )
                st.plotly_chart(fig_bar, width="stretch")

            with chart_col4:
                # Biểu đồ phân tán (Scatter) - Mối quan hệ Diện tích & Giá
                fig_scatter = px.scatter(
                    filtered_df, 
                    x='area', 
                    y='price_billion', 
                    color='category', 
                    title='Mối quan hệ giữa Diện tích và Giá tiền',
                    opacity=0.6, # Làm mờ chấm để thấy các điểm trùng nhau
                    hover_data=['district'],
                    labels={'area': 'Diện tích (m2)', 'price_billion': 'Giá (Tỷ VNĐ)', 'category': 'Loại BĐS'}
                )
                st.plotly_chart(fig_scatter, width="stretch")

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

    # --- KHỞI TẠO BIẾN SESSION STATE (Lưu trạng thái) ---
    if "lat" not in st.session_state:
        st.session_state.lat = 10.938  
        st.session_state.lon = 106.767 
        st.session_state.schools = 1
        st.session_state.markets = 1
        st.session_state.hospitals = 0
        st.session_state.province = "Hồ Chí Minh"
        st.session_state.district = "Quận 1"

    st.markdown("### 📍 Bước 1: Chọn vị trí Bất Động Sản trên bản đồ")
    st.info("💡 Click vào bản đồ: Hệ thống sẽ tự động quét Quận/Huyện, Tỉnh/Thành phố và đếm trường học, siêu thị xung quanh!")

    m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=13)
    folium.Marker([st.session_state.lat, st.session_state.lon], tooltip="Vị trí đang chọn", icon=folium.Icon(color="red")).add_to(m)
    map_data = st_folium(m, height=400, width=1000)

    # --- XỬ LÝ KHI CLICK VÀO BẢN ĐỒ ---
    if map_data and map_data.get('last_clicked'):
        c_lat = map_data['last_clicked']['lat']
        c_lon = map_data['last_clicked']['lng']
        
        if c_lat != st.session_state.lat or c_lon != st.session_state.lon:
            st.session_state.lat = c_lat
            st.session_state.lon = c_lon
            
            with st.spinner("⏳ Đang phân tích địa chỉ và quét tiện ích xung quanh..."):
                # 1. Quét Địa Chỉ
                address_dict = get_address_from_coords(c_lat, c_lon)
                st.session_state.province, st.session_state.district = match_location_from_api(address_dict)
                
                # 2. Quét Tiện Ích
                school_tags =[("amenity", "school"), ("amenity", "kindergarten"), ("amenity", "college")]
                market_tags =[("amenity", "marketplace"), ("shop", "supermarket"), ("shop", "convenience")]
                hospital_tags = [("amenity", "hospital"), ("amenity", "clinic")]
                
                st.session_state.schools = get_poi_count(c_lat, c_lon, 1000, school_tags)
                st.session_state.markets = get_poi_count(c_lat, c_lon, 1000, market_tags)
                st.session_state.hospitals = get_poi_count(c_lat, c_lon, 2000, hospital_tags)
            
            st.rerun() # Refresh lại trang ngay lập tức để cập nhật số liệu

    st.divider()
    st.markdown("### 📝 Bước 2: Nhập các thông tin chi tiết khác")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**1. Hành chính & Pháp lý**")
        
        # Lấy danh sách Tỉnh/Thành phố
        provinces_list = list(LOCATION_MAPPING.keys())
        current_prov = st.session_state.province if st.session_state.province in provinces_list else "Hồ Chí Minh"
        
        # Chọn Tỉnh / Thành Phố
        province = st.selectbox("Tỉnh/Thành phố", provinces_list, index=provinces_list.index(current_prov))
        
        # --- Logic tự động thay đổi Quận/Huyện khi user đổi Tỉnh bằng tay ---
        if province != st.session_state.province:
            st.session_state.province = province
            st.session_state.district = LOCATION_MAPPING[province][0] # Đổi tỉnh -> reset quận về vị trí 0
            st.rerun()
            
        # Lấy danh sách Quận/Huyện DỰA TRÊN Tỉnh đang chọn
        districts_list = LOCATION_MAPPING[st.session_state.province]
        current_dist = st.session_state.district if st.session_state.district in districts_list else districts_list[0]
        
        # Chọn Quận / Huyện
        district = st.selectbox("Quận/Huyện", districts_list, index=districts_list.index(current_dist))
        
        # Cập nhật state nếu user đổi tay Quận/Huyện
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

    if st.button("🚀 BẮT ĐẦU DỰ ĐOÁN GIÁ", type="primary", width="stretch"):
        input_data = pd.DataFrame({
            'area':[area],
            'category': [category],
            'latitude': [st.session_state.lat], 
            'longitude': [st.session_state.lon],
            'district': [st.session_state.district], # Đã lấy từ session state chuẩn
            'province': [st.session_state.province], # Đã lấy từ session state chuẩn
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