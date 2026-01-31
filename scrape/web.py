# author:  Huy
# created: 11:25:27 18/01/2026
# updated: Fix focus stealing & anti-bot detection

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import csv
import re
import os
import random
import zlib
import base64

# --- CẤU HÌNH ---
FILE_NAME = "data.csv"
# URL gốc (Lưu ý: Code sẽ tự động xử lý phần phân trang /p...)
URL_BASE = "https://batdongsan.com.vn/nha-dat-ban-tp-hcm/p790"
START_PAGE = 790
END_PAGE = 1000

FIELDNAMES = [
    'post_id', 'post_title', 'url', 'post_type', 'verified_status',
    'published_date', 'expiration_date', 'crawled_date',
    'seller_name', 'seller_type', 'province', 'district', 'ward', 'street',
    'project_name', 'address_full', 'latitude', 'longitude', 'google_maps_link',
    'category', 'price_total', 'area', 'price_per_m2', 'legal_status',
    'description_compressed', 'frontage', 'road_width', 'num_floors',
    'num_bedrooms', 'num_toilets', 'house_direction', 'balcony_direction',
    'furniture'
]

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---

def compress_text(text):
    if not text or text == "N/A": return "N/A"
    try:
        data = text.encode('utf-8')
        compressed = zlib.compress(data)
        return base64.b64encode(compressed).decode('utf-8')
    except:
        return text

def clean_number(text):
    if not text: return 0.0
    try:
        num = re.findall(r"[-+]?\d*\.\d+|\d+", text.replace(',', '.'))
        return float(num[0]) if num else 0.0
    except:
        return 0.0

def convert_price_to_vnd(price_str):
    if not price_str: return 0.0
    val = clean_number(price_str)
    if 'tỷ' in price_str.lower(): return val * 1_000_000_000
    if 'triệu' in price_str.lower(): return val * 1_000_000
    return val

def parse_address(address_str):
    parts = [p.strip() for p in address_str.split(',')]
    res = {"street": "N/A", "ward": "N/A", "district": "N/A", "province": "N/A"}
    try:
        if len(parts) >= 1: res["province"] = parts[-1]
        if len(parts) >= 2: res["district"] = parts[-2]
        if len(parts) >= 3: res["ward"] = parts[-3]
        if len(parts) >= 4: res["street"] = parts[-4]
    except: pass
    return res

def scrape_post_detail(driver, url):
    """
    Hàm này nhận driver và url. 
    Nó sẽ tự load url trên tab hiện tại (không switch tab).
    """
    try:
        driver.get(url)
        # Chờ tiêu đề xuất hiện để chắc chắn trang đã load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "re__pr-title")))
    except:
        # Nếu timeout hoặc lỗi load trang
        return None

    all_props = {}
    
    # 1. Lấy thông tin tóm tắt
    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-short-info-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "title").text.strip()
            val = item.find_element(By.CLASS_NAME, "value").text.strip()
            all_props[name] = val
    except: pass

    # 2. Lấy đặc điểm
    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-specs-content-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "re__pr-specs-content-item-title").text.strip()
            val = item.find_element(By.CLASS_NAME, "re__pr-specs-content-item-value").text.strip()
            all_props[name] = val
    except: pass

    # 3. Lấy cấu hình tin
    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-config-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "title").text.strip()
            val = item.find_element(By.CLASS_NAME, "value").text.strip()
            all_props[name] = val
    except: pass

    # Tiêu đề & Địa chỉ
    post_title = "N/A"
    try: post_title = driver.find_element(By.CLASS_NAME, "re__pr-title").text
    except: pass

    address_full = "N/A"
    try: address_full = driver.find_element(By.CLASS_NAME, "re__pr-short-description").text
    except: pass
    addr_info = parse_address(address_full)

    # Giá & Diện tích
    price_total = convert_price_to_vnd(all_props.get("Khoảng giá", "N/A"))
    area_val = clean_number(all_props.get("Diện tích", "N/A"))
    price_per_m2 = (price_total / area_val) if area_val > 0 else 0

    # Map
    lat, lon, gmap = "0", "0", "N/A"
    try:
        iframe = driver.find_element(By.CSS_SELECTOR, ".re__pr-map iframe")
        src = iframe.get_attribute("data-src") or iframe.get_attribute("src")
        match = re.search(r'q=([-+]?\d*\.\d+),([-+]?\d*\.\d+)', src)
        if match:
            lat, lon = match.group(1), match.group(2)
            gmap = f"https://www.google.com/maps?q={lat},{lon}"
    except: pass

    # Seller Info
    seller_name, seller_type = "N/A", "N/A"
    try:
        els = driver.find_elements(By.CLASS_NAME, "re__contact-name")
        for el in els:
            t = el.get_attribute("title") or el.text.strip()
            if t: 
                seller_name = t
                break
    except: pass
    
    try:
        if driver.find_elements(By.CLASS_NAME, "re__ldp-agent-desc"):
            seller_type = "Môi giới chuyên nghiệp"
    except: pass

    # Project & Verify
    project_name = "N/A"
    try: project_name = driver.find_element(By.CLASS_NAME, "re__project-title").text.strip()
    except: pass
    
    verified = False
    if driver.find_elements(By.CLASS_NAME, "re__card-image-verified"): verified = True

    # Category
    category = "N/A"
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "re__breadcrumb")
        category = breadcrumb.find_elements(By.TAG_NAME, "a")[-1].text.strip().split(" tại")[0]
    except: pass

    # Description
    desc = "N/A"
    try: desc = driver.find_element(By.CLASS_NAME, "re__detail-content").text
    except: pass

    return {
        'post_id': all_props.get("Mã tin", "N/A"),
        'post_title': post_title,
        'url': url,
        'post_type': all_props.get("Loại tin", "N/A"),
        'verified_status': verified,
        'published_date': all_props.get("Ngày đăng", "N/A"),
        'expiration_date': all_props.get("Ngày hết hạn", "N/A"),
        'crawled_date': datetime.now().strftime("%Y-%m-%d"),
        'seller_name': seller_name,
        'seller_type': seller_type,
        'province': addr_info["province"],
        'district': addr_info["district"],
        'ward': addr_info["ward"],
        'street': addr_info["street"],
        'project_name': project_name,
        'address_full': address_full,
        'latitude': lat,
        'longitude': lon,
        'google_maps_link': gmap,
        'category': category,
        'price_total': price_total,
        'area': area_val,
        'price_per_m2': price_per_m2,
        'legal_status': all_props.get("Pháp lý", "N/A"),
        'description_compressed': compress_text(desc),
        'frontage': all_props.get("Mặt tiền", "N/A"),
        'road_width': all_props.get("Đường vào", "N/A"),
        'num_floors': all_props.get("Số tầng", "N/A"),
        'num_bedrooms': all_props.get("Số phòng ngủ", "N/A"),
        'num_toilets': all_props.get("Số phòng tắm, vệ sinh", "N/A"),
        'house_direction': all_props.get("Hướng nhà", "N/A"),
        'balcony_direction': all_props.get("Hướng ban công", "N/A"),
        'furniture': all_props.get("Nội thất", "N/A")
    }

def main():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-popup-blocking")
    
    # --- QUAN TRỌNG: Đẩy trình duyệt ra khỏi màn hình thay vì dùng headless ---
    # Toạ độ -10000 đảm bảo bạn không thấy nó, nhưng nó vẫn là cửa sổ thật
    options.add_argument("--window-position=-10000,0") 
    # ------------------------------------------------------------------------

    print("Đang khởi động trình duyệt (Chế độ ẩn off-screen)...")
    driver = uc.Chrome(options = options, version_main = 143)

    # Tạo file CSV nếu chưa có
    if not os.path.isfile(FILE_NAME):
        with open(FILE_NAME, 'w', encoding='utf-8-sig', newline='') as f:
            csv.DictWriter(f, fieldnames = FIELDNAMES).writeheader()
    
    current_page = START_PAGE

    try:
        while current_page <= END_PAGE:
            # Xây dựng URL cho page hiện tại
            # Xóa đoạn /p... cũ trong URL_BASE (nếu có) và thêm page mới
            base_clean = re.sub(r'/p\d+', '', URL_BASE)
            # URL batdongsan thường dạng: .../p2, .../p3
            page_url = f"{base_clean}/p{current_page}"

            print(f"\n--- ĐANG XỬ LÝ TRANG {current_page} ---")
            print(f"Link danh sách: {page_url}")
            
            # 1. Load trang danh sách (trên tab duy nhất)
            driver.get(page_url)
            time.sleep(random.uniform(3, 5)) # Chờ load

            # 2. Tìm tất cả link chi tiết
            elements = driver.find_elements(By.CSS_SELECTOR, "a.js__product-link-for-product-id")
            # Lọc trùng và lấy href
            links = list(set([e.get_attribute("href") for e in elements if e.get_attribute("href")]))
            
            print(f"-> Tìm thấy {len(links)} tin. Bắt đầu cào chi tiết...")

            if not links:
                print("⚠️ Không tìm thấy tin nào. Có thể đã hết trang hoặc bị chặn IP.")
                # Thử check xem có phải bị cloudflare không
                if "challenge" in driver.title.lower():
                    print("!!! ĐÃ BỊ CHẶN BỞI CLOUDFLARE !!!")
                    input("Vui lòng mở trình duyệt lên xử lý Captcha rồi nhấn Enter...")
                else:
                    # Nếu không có link nào thì có thể dừng hoặc thử lại
                    pass

            # 3. Duyệt từng link (Load đè lên tab hiện tại)
            for idx, link in enumerate(links):
                try:
                    print(f"  [{idx+1}/{len(links)}] {link} ... ", end="", flush=True)
                    
                    # Gọi hàm cào (hàm này sẽ driver.get(link))
                    data = scrape_post_detail(driver, link)
                    
                    if data:
                        with open(FILE_NAME, 'a', encoding='utf-8-sig', newline='') as f:
                            csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(data)
                        print("OK")
                    else:
                        print("BỎ QUA (Lỗi load)")
                    
                    # Sleep để tránh bị chặn
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"LỖI: {e}")

            # Sau khi xong hết link của trang này, tăng số trang và vòng lặp while quay lại từ đầu
            # để load trang danh sách tiếp theo.
            current_page += 1

    except KeyboardInterrupt:
        print("\nNgười dùng dừng chương trình.")
    except Exception as e:
        print(f"\nLỗi chương trình chính: {e}")
    finally:
        driver.quit()
        print("Đã đóng trình duyệt.")

if __name__ == "__main__":
    main()