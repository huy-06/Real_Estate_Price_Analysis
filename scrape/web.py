"""
Module thực hiện thu thập dữ liệu bất động sản từ website batdongsan.com.vn.
Sử dụng undetected_chromedriver để vượt qua các cơ chế chống bot và lưu trữ
dữ liệu dưới dạng CSV với nội dung mô tả được nén để tối ưu dung lượng.
"""

import base64
import csv
import os
import random
import re
import time
import zlib
from datetime import datetime

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Cấu hình hệ thống
FILE_NAME = "data.csv"
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


def compress_text(text):
    """Nén văn bản bằng zlib và mã hóa base64 để lưu vào CSV."""
    if not text or text == "N/A":
        return "N/A"
    try:
        data = text.encode('utf-8')
        compressed = zlib.compress(data)
        return base64.b64encode(compressed).decode('utf-8')
    except (zlib.error, UnicodeEncodeError):
        return text


def clean_number(text):
    """Trích xuất giá trị số từ chuỗi văn bản bất kỳ."""
    if not text:
        return 0.0
    try:
        num = re.findall(r"[-+]?\d*\.\d+|\d+", text.replace(',', '.'))
        return float(num[0]) if num else 0.0
    except (ValueError, IndexError):
        return 0.0


def convert_price_to_vnd(price_str):
    """Chuyển đổi các đơn vị giá (tỷ, triệu) về đơn vị VND."""
    if not price_str:
        return 0.0
    val = clean_number(price_str)
    price_lower = price_str.lower()
    if 'tỷ' in price_lower:
        return val * 1_000_000_000
    if 'triệu' in price_lower:
        return val * 1_000_000
    return val


def parse_address(address_str):
    """Phân tách chuỗi địa chỉ thành các cấp hành chính."""
    parts = [p.strip() for p in address_str.split(',')]
    res = {"street": "N/A", "ward": "N/A", "district": "N/A", "province": "N/A"}
    try:
        if len(parts) >= 1:
            res["province"] = parts[-1]
        if len(parts) >= 2:
            res["district"] = parts[-2]
        if len(parts) >= 3:
            res["ward"] = parts[-3]
        if len(parts) >= 4:
            res["street"] = parts[-4]
    except (IndexError, AttributeError):
        pass
    return res


def scrape_post_detail(driver, url):
    """Truy cập và trích xuất thông tin chi tiết của một tin đăng."""
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "re__pr-title"))
        )
    except Exception:
        return None

    all_props = {}
    
    # Thu thập các thuộc tính từ các bảng thông tin khác nhau
    selectors = [
        (By.CLASS_NAME, "re__pr-short-info-item", "title", "value"),
        (By.CLASS_NAME, "re__pr-specs-content-item", "re__pr-specs-content-item-title", "re__pr-specs-content-item-value"),
        (By.CLASS_NAME, "re__pr-config-item", "title", "value")
    ]

    for container_selector, name_class, val_class in selectors:
        try:
            items = driver.find_elements(container_selector[0], container_selector[1])
            for item in items:
                name = item.find_element(By.CLASS_NAME, name_class).text.strip()
                val = item.find_element(By.CLASS_NAME, val_class).text.strip()
                all_props[name] = val
        except Exception:
            continue

    # Xử lý thông tin cơ bản
    post_title = "N/A"
    try:
        post_title = driver.find_element(By.CLASS_NAME, "re__pr-title").text
    except Exception:
        pass

    address_full = "N/A"
    try:
        address_full = driver.find_element(By.CLASS_NAME, "re__pr-short-description").text
    except Exception:
        pass
    addr_info = parse_address(address_full)

    # Tính toán giá và diện tích
    price_total = convert_price_to_vnd(all_props.get("Khoảng giá", "N/A"))
    area_val = clean_number(all_props.get("Diện tích", "N/A"))
    price_per_m2 = (price_total / area_val) if area_val > 0 else 0

    # Tọa độ bản đồ
    lat, lon, gmap = "0", "0", "N/A"
    try:
        iframe = driver.find_element(By.CSS_SELECTOR, ".re__pr-map iframe")
        src = iframe.get_attribute("data-src") or iframe.get_attribute("src")
        match = re.search(r'q=([-+]?\d*\.\d+),([-+]?\d*\.\d+)', src)
        if match:
            lat, lon = match.group(1), match.group(2)
            gmap = f"https://www.google.com/maps?q={lat},{lon}"
    except Exception:
        pass

    # Thông tin người bán
    seller_name, seller_type = "N/A", "N/A"
    try:
        contact_elements = driver.find_elements(By.CLASS_NAME, "re__contact-name")
        for el in contact_elements:
            t = el.get_attribute("title") or el.text.strip()
            if t:
                seller_name = t
                break
        if driver.find_elements(By.CLASS_NAME, "re__ldp-agent-desc"):
            seller_type = "Môi giới chuyên nghiệp"
    except Exception:
        pass

    # Phân loại và Mô tả
    category = "N/A"
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "re__breadcrumb")
        category = breadcrumb.find_elements(By.TAG_NAME, "a")[-1].text.strip().split(" tại")[0]
    except Exception:
        pass

    desc = "N/A"
    try:
        desc = driver.find_element(By.CLASS_NAME, "re__detail-content").text
    except Exception:
        pass

    return {
        'post_id': all_props.get("Mã tin", "N/A"),
        'post_title': post_title,
        'url': url,
        'post_type': all_props.get("Loại tin", "N/A"),
        'verified_status': bool(driver.find_elements(By.CLASS_NAME, "re__card-image-verified")),
        'published_date': all_props.get("Ngày đăng", "N/A"),
        'expiration_date': all_props.get("Ngày hết hạn", "N/A"),
        'crawled_date': datetime.now().strftime("%Y-%m-%d"),
        'seller_name': seller_name,
        'seller_type': seller_type,
        'province': addr_info["province"],
        'district': addr_info["district"],
        'ward': addr_info["ward"],
        'street': addr_info["street"],
        'project_name': all_props.get("Tên dự án", "N/A"),
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
    """Hàm điều khiển luồng chính của chương trình crawler."""
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-position=-10000,0") 

    print("Đang khởi động trình duyệt (Off-screen mode)...")
    driver = uc.Chrome(options=options, version_main=143)

    if not os.path.isfile(FILE_NAME):
        with open(FILE_NAME, 'w', encoding='utf-8-sig', newline='') as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader()
    
    current_page = START_PAGE

    try:
        while current_page <= END_PAGE:
            base_clean = re.sub(r'/p\d+', '', URL_BASE)
            page_url = f"{base_clean}/p{current_page}"

            print(f"\n--- ĐANG XỬ LÝ TRANG {current_page} ---")
            driver.get(page_url)
            time.sleep(random.uniform(3, 5))

            elements = driver.find_elements(By.CSS_SELECTOR, "a.js__product-link-for-product-id")
            links = list(set([e.get_attribute("href") for e in elements if e.get_attribute("href")]))
            
            print(f"-> Tìm thấy {len(links)} tin.")

            if not links and "challenge" in driver.title.lower():
                print("!!! ĐÃ BỊ CHẶN BỞI CLOUDFLARE !!!")
                input("Vui lòng xử lý Captcha rồi nhấn Enter...")
                continue

            for idx, link in enumerate(links):
                try:
                    print(f"  [{idx+1}/{len(links)}] {link[:50]}... ", end="", flush=True)
                    data = scrape_post_detail(driver, link)
                    
                    if data:
                        with open(FILE_NAME, 'a', encoding='utf-8-sig', newline='') as f:
                            csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(data)
                        print("OK")
                    else:
                        print("FAILED")
                    
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"LỖI: {e}")

            current_page += 1

    except KeyboardInterrupt:
        print("\nNgười dùng chủ động dừng chương trình.")
    finally:
        driver.quit()
        print("Đã đóng trình duyệt.")


if __name__ == "__main__":
    main()