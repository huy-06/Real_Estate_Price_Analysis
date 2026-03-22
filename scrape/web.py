import os, csv, re, time, random, undetected_chromedriver, base64, zlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from datetime import datetime

URL_BASE = "https://batdongsan.com.vn/nha-dat-ban-tp-hcm/p2"

FILENAME = "data.csv"

START_PAGE = 2
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

def parse_address(address):
    parts = [p.strip() for p in address.split(',')]
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
    except Exception:
        pass

    return res

def clean_number(text):
    if not text: 
        return 0.0
    
    try:
        num = re.findall(r"[-+]?\d*\.\d+|\d+", text.replace(',', '.'))
        return float(num[0]) if num else 0.0
    except:
        return 0.0

def convert_price_to_vnd(price, area):
    if not price:
        return 0
    
    val = clean_number(price)

    price = price.lower()
    if '/' in price:
        if "tỷ" in price:
            return int(val * 1_000_000_000 * area)
        if "triệu" in price:
            return int(val * 1_000_000 * area)
    else:
        if "tỷ" in price:
            return int(val * 1_000_000_000)
        if "triệu" in price:
            return int(val * 1_000_000)

    return val
    
def compress_text(text):
    if not text or text == "N/A":
        return "N/A"
    try:
        data = text.encode('utf-8')
        compressed = zlib.compress(data)
        return base64.b64encode(compressed).decode('utf-8')
    except (zlib.error, UnicodeEncodeError):
        return text


def scrape_post_detail(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver=driver, timeout=10).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "re__pr-title"))
        )
    except Exception:
        return None
    
    all_props = {}

    # Thu thập các thuộc tính từ các bảng thông tin khác nhau
    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-short-info-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "title").text.strip()
            val = item.find_element(By.CLASS_NAME, "value").text.strip()
            all_props[name] = val
    except Exception:
        pass

    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-specs-content-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "re__pr-specs-content-item-title").text.strip()
            val = item.find_element(By.CLASS_NAME, "re__pr-specs-content-item-value").text.strip()
            all_props[name] = val
    except Exception: 
        pass

    try:
        items = driver.find_elements(By.CLASS_NAME, "re__pr-config-item")
        for item in items:
            name = item.find_element(By.CLASS_NAME, "title").text.strip()
            val = item.find_element(By.CLASS_NAME, "value").text.strip()
            all_props[name] = val
    except Exception: 
        pass

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
    address_info = parse_address(address_full)

    # Tính toán giá và diện tích
    area = clean_number(all_props.get("Diện tích", "N/A"))
    price_total = convert_price_to_vnd(all_props.get("Khoảng giá", "N/A"), area)
    price_per_m2 = (price_total / area) if area > 0 else 0

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
        els = driver.find_elements(By.CLASS_NAME, "re__contact-name")
        for el in els:
            t = el.get_attribute("title") or el.text.strip()
            if t: 
                seller_name = t
                break
    except Exception:
        pass
    
    try:
        if driver.find_elements(By.CLASS_NAME, "re__ldp-agent-desc"):
            seller_type = "Môi giới chuyên nghiệp"
    except Exception:
        pass

    # Phân loại và Mô tả
    project_name = "N/A"
    try: 
        project_name = driver.find_element(By.CLASS_NAME, "re__project-title").text.strip()
    except Exception:
        pass

    
    verified = False
    if driver.find_elements(By.CLASS_NAME, "re__card-image-verified"): verified = True

    # Category
    category = "N/A"
    try:
        breadcrumb = driver.find_element(By.CLASS_NAME, "re__breadcrumb")
        category = breadcrumb.find_elements(By.TAG_NAME, "a")[-1].text.strip().split(" tại")[0]
    except Exception:
        pass

    # Description
    description = "N/A"
    try: 
        description = driver.find_element(By.CLASS_NAME, "re__detail-content").text
    except Exception:
        pass

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
        'province': address_info["province"],
        'district': address_info["district"],
        'ward': address_info["ward"],
        'street': address_info["street"],
        'project_name': all_props.get("Tên dự án", "N/A"),
        'address_full': address_full,
        'latitude': lat,
        'longitude': lon,
        'google_maps_link': gmap,
        'category': category,
        'price_total': price_total,
        'area': area,
        'price_per_m2': price_per_m2,
        'legal_status': all_props.get("Pháp lý", "N/A"),
        'description_compressed': compress_text(description),
        'frontage': float(clean_number(all_props.get("Mặt tiền", "N/A"))),
        'road_width': float(clean_number(all_props.get("Đường vào", "N/A"))),
        'num_floors': int(clean_number(all_props.get("Số tầng", "N/A"))),
        'num_bedrooms': int(clean_number(all_props.get("Số phòng ngủ", "N/A"))),
        'num_toilets': int(clean_number(all_props.get("Số phòng tắm, vệ sinh", "N/A"))),
        'house_direction': all_props.get("Hướng nhà", "N/A"),
        'balcony_direction': all_props.get("Hướng ban công", "N/A"),
        'furniture': all_props.get("Nội thất", "N/A")
    }
    

if __name__ == "__main__":
    options = undetected_chromedriver.ChromeOptions()
    
    options.add_argument("--no-sandbox") # Tắt tính năng bảo mật
    options.add_argument("--disable-dev-shm-usage") # Thay đổi cách sử dụng bộ nhớ RAM
    options.add_argument("--disable-popup-blocking") # Chặn các cửa số bật lên
    options.add_argument("--window-position=-10000,0") # Ép cửa số nằm ra khỏi màn hình

    print("Đang khỏi động trình duyệt...")

    driver = undetected_chromedriver.Chrome(options=options, version_main=145)

    if not os.path.isfile(FILENAME):
        with open(FILENAME, 'w', encoding="utf-8-sig", newline='') as f:
            csv.DictWriter(f, fieldnames=FIELDNAMES).writeheader() # In ra tên các thuộc tính ở dòng đầu tiên

    try:
        for current_page in range(START_PAGE, END_PAGE + 1):
            base_clean = re.sub(r'/p\d+', '', URL_BASE) # Cắt bỏ chỗ \p\d+ để thay số mới vào
            page_url = f"{base_clean}/p{current_page}"

            print(f"\nĐanng xử lý trang {current_page}...")

            driver.get(page_url)
            time.sleep(random.uniform(3, 5))

            elements = driver.find_elements(By.CSS_SELECTOR, "a.js__product-link-for-product-id") # Tìm các phần tử chưa link bài đăng
            links = list(set([e.get_attribute("href") for e in elements if e.get_attribute("href")])) # Rút ruột lấy link bài đăng

            print(f"-> Tìm thấy {len(links)} tin.")

            if not links and "challenge" in driver.title.lower():
                print("!!! ĐÃ BỊ CHẶN BỞI CLOUDFLARE !!!")
                input("Vui lòng xử lý Captcha rồi nhấn Enter...")
                continue

            for idx, link in enumerate(links):
                try:
                    print(f"Đang xử lý bài thứ {idx + 1}...", end="", flush=True)

                    data = scrape_post_detail(driver, link)

                    if data:
                        with open(FILENAME, 'a', encoding="utf-8-sig", newline='') as f:
                            csv.DictWriter(f, fieldnames=FIELDNAMES).writerow(data)
                        print("OK")
                    else:
                        print("FAILED")
                    
                    time.sleep(random.uniform(2, 4))

                except Exception as e:
                    print(f"LỖI: {e}")
                
            

    except KeyboardInterrupt:
        print("\nNgười dùng chủ động dừng chương trình.")
    
    finally:
        driver.quit()
        print("Đã đóng trình duyệt.")
        