# بخش اول: ایمپورت‌ها و تنظیمات کلی
import re
import time
import sqlite3
import pandas as pd
from datetime import datetime

# برای موازی‌سازی
import concurrent.futures
from math import ceil

# ---- تنظیمات Selenium ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# برای مدیریت انتظار
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# مسیر درایور کروم و تنظیمات
chrome_driver_path = r"C:\inetpub\wwwroot\flask v0.3\chromedriver-win64\chromedriver.exe"
file_path = r"C:\inetpub\wwwroot\flask v0.3\static\scrap.xlsx"
db_name = r"C:\inetpub\wwwroot\flask v0.3\datasitenews5.db"
# بخش دوم: دیکشنری رنگ‌ها و توابع کمکی

# --- فرهنگ‌لغت رنگ‌ها ---
color_map = {
    "hamrahtel": {
        "خاکستری(گرافیت)": "Graphite",
        "ذغالی": "Graphite",
        "خاکستری": "Gray",
        "مشکی": "Black",
        "نقره ای": "Silver",
        "صورتی": "Pink",
        "ابی": "Blue",
        "آبی": "Blue",
        "سفید": "white",
        "ابی روشن": "Blue",
        "سبز": "Green",
        "طلایی": "Gold",
        "بنفش": "Violet",
        "زرد": "Yellow",
        "ابی تیره": "Navy",
        "آبی تیره": "Navy",
        "سرمه ای": "Navy",
        "یاسی": "Lilac",
        "لیمویی": "Lime",
        "مشکی تیتانیوم": "Gray",
        "خاکستری تیتانیوم": "Titanium Gray",
        "آبی روشن": "Blue",
        "مشکی آبی": "Navy",
        "مشکی ابی": "Navy",
        "کرم": "Cream",
    },
    "farnaa": {
        "خاکستری": "Gray",
        "ذغالی": "Graphite",
        "مشکی": "Black",
        "نقره ای": "Silver",
        "صورتی": "Pink",
        "ابی": "Blue",
        "آبی": "Blue",
        "سفید": "white",
        "ابی روشن ": "Blue",
        "آبی روشن": "Blue",
        "سبز": "Green",
        "طلایی": "Gold",
        "بنفش ": "Violet",
        "بنفش روشن": "Violet",
        "زرد": "Yellow",
        "ابی تیره ": "Navy",
        "آبی تیره": "Navy",
        "مشکی آبی": "Navy",
        "سرمه ای": "Navy",
        "یاسی": "Lilac",
        "لیمویی": "Lime",
        "مشکی تیتانیوم": "Gray",
        "خاکستری تیتانیوم": "Titanium Gray",
        "استارلایت(starlight)": " white",
        "کرم": "Cream",
        "تیتانیوم - طبیعی": "Natural Titanium",
        "تیتانیوم - صحرایی": "Desert Titanium",
        "تیتانیوم - مشکی": "Black Titanium",
        "تیتانیوم - سفید": "White Titanium",
    },
    "aasood": {
        "خاکستری": "Gray",
        "طوسی": "Gray",
        "ذغالی": "Graphite",
        "مشکی": "Black",
        "نقره ای": "Silver",
        "صورتی": "Pink",
        "ابی": "Blue",
        "آبی": "Blue",
        "سفید": "white",
        "ابی روشن ": "Blue",
        "آبی روشن": "Blue",
        "آبی یخی": "Blue",
        "سبز": "Green",
        "طلایی": "Gold",
        "طلايی": "Gold",
        "بنفش ": "Violet",
        "بنفش": "Violet",
        "بنفش روشن": "Violet",
        "زرد": "Yellow",
        "ابی تیره ": "Navy",
        "آبی تیره": "Navy",
        "مشکی آبی": "Navy",
        "سرمه ای": "Navy",
        "یاسی": "Lilac",
        "لیمویی": "Lime",
        "مشکی تیتانیوم": "Gray",
        "خاکستری تیتانیوم": "Titanium Gray",
        "استارلایت(starlight)": " white",
        "کرم": "Cream",
        "طلایی": "Gold",
        # ... سایر رنگ‌های احتمالی ...
    },
    "technobusiness": {
        "خاکستری": "Gray",
        "خاکستری روشن": "Gray",
        "خاکستری تیره": "Graphite",
        "طوسی": "Gray",
        "ذغالی": "Graphite",
        "مشکی": "Black",
        "نقره ای": "Silver",
        "صورتی": "Pink",
        "ابی": "Blue",
        "آبی": "Blue",
        "سفید": "white",
        "ابی روشن ": "Blue",
        "آبی روشن": "Blue",
        "آبی یخی": "Blue",
        "سبز": "Green",
        "سبز روشن": "Green",
        "طلایی": "Gold",
        "بنفش ": "Violet",
        "زرد": "Yellow",
        "ابی تیره ": "Navy",
        "آبی تیره": "Navy",
        "مشکی آبی": "Navy",
        "سرمه ای": "Navy",
        "سرمه‌ای": "Navy",
        "یاسی": "Lilac",
        "لیمویی": "Lime",
        "مشکی تیتانیوم": "Gray",
        "خاکستری تیتانیوم": "Titanium Gray",
        "استارلایت(starlight)": " white",
        "کرم": "Cream",
    },
    "kasrapars": {
        "خاکستری": "Gray",
        "خاکستری روشن": "Gray",
        "خاکستری تیره": "Graphite",
        "طوسی": "Gray",
        "ذغالی": "Graphite",
        "مشکی": "Black",
        "نقره ای": "Silver",
        "صورتی": "Pink",
        "ابی": "Blue",
        "آبی": "Blue",
        "سفید": "white",
        "ابی روشن ": "Blue",
        "آبی روشن": "Blue",
        "آبی یخی": "Blue",
        "سبز": "Green",
        "سبز روشن": "Green",
        "طلایی": "Gold",
        "بنفش ": "Violet",
        "زرد": "Yellow",
        "ابی تیره ": "Navy",
        "آبی تیره": "Navy",
        "مشکی آبی": "Navy",
        "سرمه ای": "Navy",
        "سرمه‌ای": "Navy",
        "یاسی": "Lilac",
        "لیمویی": "Lime",
        "مشکی تیتانیوم": "Gray",
        "خاکستری تیتانیوم": "Titanium Gray",
        "استارلایت(starlight)": " white",
        "کرم": "Cream",
    }
}


def normalize_color(color_name, site_name, custom_color_map=None):
    if custom_color_map is not None:
        # اگر نگاشت اختصاصی برای محصول تنظیم شده است
        return custom_color_map.get(color_name, color_name)
    # در غیر این صورت از نگاشت‌های سراسری استفاده کن
    return color_map.get(site_name, {}).get(color_name, color_name)



def extract_price(price_text):
    """
    حذف کاراکترهای غیرعددی از رشته‌ی قیمت و برگرداندن آن با فرمت سه‌رقم سه‌رقم.
    اگر قیمتی پیدا نشود، مقدار '0' برمی‌گرداند.
    """
    price_numbers = re.findall(r'\d+', price_text)
    if price_numbers:
        price = int(''.join(price_numbers))
        return "{:,}".format(price)
    return "0"


def find_min_price(*prices):
    """
    پیدا کردن کمترین قیمت (غیر از صفر) بین تمام ورودی‌ها.
    اگر همه صفر بودند، نهایتاً '0' برمی‌گرداند.
    """
    def to_int(p):
        return int(p.replace(',', '').replace(' تومان', '')) if p != "0" else float('inf')
    int_prices = [to_int(price) for price in prices]
    min_val = min(int_prices)
    return "{:,}".format(min_val) if min_val != float('inf') else "0"
# بخش سوم: تابع ساخت یک نوار پیشرفت ساده (ASCII Progress Bar)

def make_ascii_bar(progress_ratio, length=30):
    """
    ساخت یک نوار پیشرفت ساده به صورت ASCII.
    مثلاً اگر progress_ratio=0.5 و length=10 بشود [#####-----] 50.00%
    """
    filled_length = int(progress_ratio * length)
    bar = "#" * filled_length + "-" * (length - filled_length)
    return f"[{bar}] {progress_ratio * 100:.2f}%"
# بخش چهارم: تابع اسکرپ هر چانک (قسمت اول: آماده‌سازی)

def scrape_chunk(products_chunk, chunk_index, total_chunks, total_products):
    """
    این تابع روی هر Process جداگانه اجرا می‌شود.
    در این تابع:
      1) درایور Selenium ساخته می‌شود.
      2) برای هر محصول در chunk، اطلاعات از 5 سایت گرفته می‌شود.
      3) نتیجه به صورت لیست برگردانده می‌شود.
    """

    # پیکربندی Selenium در هر پراسس
    chrome_options = Options()
    # اگر نمی‌خواهید مرورگر باز شود، خط زیر را غیرفعال نکنید:
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")

    # برای کم‌کردن لاگ‌های اضافی
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)

    chunk_data = []
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M')

    # تعداد محصولات در این چانک
    chunk_size = len(products_chunk)
# بخش پنجم: تابع اسکرپ هر چانک (قسمت دوم: حلقه‌ی محصولات + اسکرپ Hamrahtel)

    for i, product in enumerate(products_chunk, start=1):
    # --------------------------- (حذف خطوط مربوط به چاپ درصد در هر محصول) ---------------------------
    # دیگر در اینجا درصد چاپ نمی‌شود.

        # --- شروع اسکرپ ---
        model = product["model"]
        category = product["category"]
        url_hamrahtel = product["urls"].get("hamrahtel", "")
        url_farnaa = product["urls"].get("farnaa", "")
        url_aasood = product["urls"].get("aasood", "")
        url_technobusiness = product["urls"].get("technobusiness", "")
        url_kasrapars = product["urls"].get("kasrapars", "")

        # ساخت دیکشنری برای نگهداری قیمت‌ها
        colors_prices = {}
        # ساختار مثال:
        # {
        #   'Gray': {
        #       "قیمت همراه‌تل": "100,000",
        #       "قیمت فرنا": "120,000",
        #       ...
        #   },
        #   ...
        # }

        # --- اسکرپ Hamrahtel ---
        try:
            if url_hamrahtel:
                driver.get(url_hamrahtel)
                products_hamrahtel = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.mantine-58jjq9'))
                )
                for product_item in products_hamrahtel:
                    try:
                        color_el = product_item.find_element(By.CSS_SELECTOR, '.mantine-1r6p0m0 .mantine-Text-root')
                        price_el = product_item.find_element(By.CSS_SELECTOR, '.mantine-kigrcs .mantine-16h1mip')
                        color_text = color_el.text.strip()
                        price_text = price_el.text.strip()
                        price_val = extract_price(price_text)

                        # دریافت نگاشت اختصاصی در صورت تعریف شده
                        custom_map = product.get("custom_color_map")
                        normalized_color = normalize_color(color_text, "hamrahtel", custom_map)

                        if normalized_color not in colors_prices:
                            colors_prices[normalized_color] = {
                                "قیمت همراه‌تل": price_val,
                                "قیمت فرنا": "0",
                                "قیمت آسوود": "0",
                                "قیمت تکنو بیزینس": "0",
                                "قیمت کسری پارس": "0"
                            }
                        else:
                            colors_prices[normalized_color]["قیمت همراه‌تل"] = price_val
                    except:
                        pass
        except:
            pass

        # --- اسکرپ Farnaa ---
        try:
            if url_farnaa:
                driver.get(url_farnaa)
                # پیدا کردن تمام دکمه‌های رنگ
                color_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.js-product-variants li.ui-variant input.js-variant_selector'))
                )

                for button in color_buttons:
                    attempt = 0
                    max_attempts = 3  # حداکثر تعداد تلاش برای کلیک روی هر دکمه

                    while attempt < max_attempts:
                        attempt += 1

                        # اسکرول به دکمه
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)  # افزایش زمان تاخیر

                        # شبیه‌سازی کلیک و رویداد change
                        driver.execute_script("""
                            arguments[0].click();
                            arguments[0].checked = true;
                            var event = new Event('change', { bubbles: true });
                            arguments[0].dispatchEvent(event);
                        """, button)

                        # صبر برای به‌روزرسانی عنصر قیمت
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.c-product_price-real.price span'))
                        )

                        # استخراج قیمت جدید
                        new_price_text = driver.find_element(By.CSS_SELECTOR, 'div.c-product_price-real.price span').text.strip()
                        price_val = extract_price(new_price_text)
                        color_name = button.get_attribute('data-id')
                        custom_map = product.get("custom_color_map")
                        normalized_color = normalize_color(color_name, "farnaa", custom_map)

                        # ذخیره قیمت در دیکشنری
                        if normalized_color not in colors_prices:
                            colors_prices[normalized_color] = {
                                "قیمت همراه‌تل": "0",
                                "قیمت فرنا": price_val,
                                "قیمت آسوود": "0",
                                "قیمت تکنو بیزینس": "0",
                                "قیمت کسری پارس": "0"
                            }
                        else:
                            if price_val != "0":
                                colors_prices[normalized_color]["قیمت فرنا"] = price_val
                        break
        except:
            pass

        # --- اسکرپ Aasood ---
        try:
            if url_aasood:
                driver.get(url_aasood)
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product-specification_colors__RpWqi"))
                )
                color_items = driver.find_elements(By.CSS_SELECTOR, ".product-specification_colors__RpWqi .product-specification_colorItem__Wn9OO")
                for item in color_items:
                    driver.execute_script("arguments[0].click();", item)
                    price_el = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".price-comp_priceComp__value__osMF2"))
                    )
                    price_text = price_el.text.replace("\n", " ")
                    price_val = extract_price(price_text)

                    label = driver.find_element(By.CSS_SELECTOR, ".product-specification_colors__RpWqi label")
                    color_parts = label.text.split(":")
                    color_name = color_parts[1].strip() if len(color_parts) > 1 else label.text.strip()

                    custom_map = product.get("custom_color_map")
                    normalized_color = normalize_color(color_name, "aasood", custom_map)
                    if normalized_color not in colors_prices:
                        colors_prices[normalized_color] = {
                            "قیمت همراه‌تل": "0",
                            "قیمت فرنا": "0",
                            "قیمت آسوود": price_val,
                            "قیمت تکنو بیزینس": "0",
                            "قیمت کسری پارس": "0"
                        }
                    else:
                        if price_val != "0":
                            colors_prices[normalized_color]["قیمت آسوود"] = price_val
        except:
            pass

        # --- اسکرپ Technolifeb2b (TechnoBusiness) ---
        try:
            if url_technobusiness:
                driver.get(url_technobusiness)
                color_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'items-center') and contains(@class, 'gap-2.5')]//div[@class='cursor-pointer']")
                for color_element in color_elements:
                    driver.execute_script("arguments[0].scrollIntoView(true);", color_element)
                    driver.execute_script("arguments[0].click();", color_element)

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'justify-end') and contains(@class, 'px-4')]//p[contains(@class, 'text-[19px]')]"))
                    )

                    color_name = color_element.find_element(By.XPATH, ".//p").text.strip()
                    price_element = driver.find_element(By.XPATH, "//div[contains(@class, 'justify-end') and contains(@class, 'px-4')]//p[contains(@class, 'text-[19px]')]")
                    price_val = extract_price(price_element.text.strip())

                    custom_map = product.get("custom_color_map")
                    normalized_color = normalize_color(color_name, "technobusiness", custom_map)
                    if normalized_color not in colors_prices:
                        colors_prices[normalized_color] = {
                            "قیمت همراه‌تل": "0",
                            "قیمت فرنا": "0",
                            "قیمت آسوود": "0",
                            "قیمت تکنو بیزینس": price_val,
                            "قیمت کسری پارس": "0"
                        }
                    else:
                        if price_val != "0":
                            colors_prices[normalized_color]["قیمت تکنو بیزینس"] = price_val
        except:
            pass

        # --- اسکرپ Kasra Pars (نسخه جدید) ---
        try:
            if url_kasrapars:
                driver.get(url_kasrapars)

                wait_kasra = WebDriverWait(driver, 15)

                # اگر نام محصول در h1 باشد (اختیاری، در صورت نیاز بخوانید):
                try:
                    model_element = wait_kasra.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.mb-3")))
                    kasra_product_name = model_element.text.strip()
                except:
                    kasra_product_name = "نامشخص"

                # صبر برای لود شدن لیست رنگ‌ها
                try:
                    color_container = wait_kasra.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".t-row.gap-4"))
                    )
                except:
                    # اگر پیدانشد، رد می‌کنیم
                    pass
                else:
                    # پیدا کردن تمام رنگ‌های موجود
                    color_divs = color_container.find_elements(By.CSS_SELECTOR, "div.cursor-pointer")

                    # حلقه روی هر رنگ
                    for index in range(len(color_divs)):
                        # بازخوانی المنت‌ها (جلوگیری از StaleElement)
                        color_divs = color_container.find_elements(By.CSS_SELECTOR, "div.cursor-pointer")

                        if index >= len(color_divs):
                            break

                        color_div = color_divs[index]
                        # گرفتن نام رنگ از data-tip
                        color_name = color_div.get_attribute("data-tip")

                        # اسکرول به عنصر و کلیک
                        driver.execute_script("arguments[0].scrollIntoView(true);", color_div)
                        color_div.click()

                        time.sleep(2)  # تاخیر برای آپدیت قیمت

                        # دریافت قیمت پس از کلیک
                        try:
                            price_element = wait_kasra.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "span.text-sm.lg\\:text-base.font-medium.text-black"))
                            )
                            price_val = extract_price(price_element.text.strip())
                        except:
                            price_val = "0"

                        custom_map = product.get("custom_color_map")
                        normalized_color = normalize_color(color_name, "kasrapars", custom_map)

                        # وارد کردن قیمت در دیکشنری
                        if normalized_color not in colors_prices:
                            colors_prices[normalized_color] = {
                                "قیمت همراه‌تل": "0",
                                "قیمت فرنا": "0",
                                "قیمت آسوود": "0",
                                "قیمت تکنو بیزینس": "0",
                                "قیمت کسری پارس": price_val
                            }
                        else:
                            if price_val != "0":
                                colors_prices[normalized_color]["قیمت کسری پارس"] = price_val
        except:
            pass

        # --- پایان تابع اسکرپ هر چانک و بازگشت نتایج ---

        # --- ساخت لیست نهایی از colors_prices ---
        for color, prices in colors_prices.items():
            min_price = find_min_price(
                prices["قیمت همراه‌تل"],
                prices["قیمت فرنا"],
                prices["قیمت آسوود"],
                prices["قیمت تکنو بیزینس"],
                prices["قیمت کسری پارس"]
            )
            chunk_data.append({
                'مدل': model,
                'دسته‌بندی': category,
                'رنگ': color,
                'قیمت همراه‌تل': prices["قیمت همراه‌تل"],
                'قیمت فرنا': prices["قیمت فرنا"],
                'قیمت آسوود': prices["قیمت آسوود"],
                'قیمت تکنو بیزینس': prices["قیمت تکنو بیزینس"],
                'قیمت کسری پارس': prices["قیمت کسری پارس"],
                'کمترین قیمت': min_price,
                'تاریخ': current_datetime
            })

    driver.quit()
    return chunk_data

# بخش نهم: تابع chunkify و آماده‌سازی لیست محصولات + اجرای موازی

def chunkify(lst, n):
    """
    تقسیم لیست اصلی محصولات به n بخش (برای موازی‌سازی).
    اگر len(lst)=10 و n=3، سه chunk برمی‌گرداند.
    """
    k = ceil(len(lst) / n)
    for i in range(0, len(lst), k):
        yield lst[i:i + k]
if __name__ == "__main__":
    # --- نمونه محصولات برای تست ---
    products_info = [
       {
            "model": "iPhone 13 256 GB CH non Active",
            "category": "Apple",
            "urls": {
                "hamrahtel": "https://hamrahtel.com/products/1001010412",
                "farnaa": "https://farnaa.com/product/30734/mobile/apple-iphone-13-non-active-256gb-and-ram-4gb-mobile-phone",
                "aasood": "https://aasood.com/product-list/2220",
                "technobusiness": "https://www.technolifeb2b.com/product-4995/...",
                "kasrapars": ""
            }
        },
    {
        "model": "Galaxy A16 128GB / 6GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001022674",
            "farnaa": "https://farnaa.com/product/43237/mobile/samsung-galaxy-a16-4g-128gb-and-6gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010073003/Mobile-Samsung-A16-(6GB-128GB-4G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-69647/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a16-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-6-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a16-4g-1286gb"
        }
    },
    {
        "model": "Galaxy A16 128GB / 4GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/samsung-galaxy-a16-128gb-ram-4gb-vietnam",
            "farnaa": "https://farnaa.com/product/43146/mobile/samsung-galaxy-a16-4g-128gb-and-4gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010073004/Mobile-Samsung-A16-(4GB-128GB-4G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-69646/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a16-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-4-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a16-4g-1284gb"
        }
    },
    {
        "model": "Galaxy A16 256GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/samsung-galaxy-a16-256gb-ram-8gb-vietnam",
            "farnaa": "https://farnaa.com/product/43236/mobile/samsung-galaxy-a16-4g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010073005/Mobile-Samsung-A16-(8GB-256GB-4G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-69649/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a16-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A06 64GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001019685",
            "farnaa": "https://farnaa.com/product/43026/mobile/samsung-galaxy-a06-64gb-and-4gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010069001/Mobile-Samsung-A06-(4GB-64GB-4G)-China",
            "technobusiness": "https://www.technolifeb2b.com/product-57991/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a06-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-64-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-4-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a06-4g-644gb"
        }
    },
    {
        "model": "Galaxy A05 64GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32443/mobile/samsung-galaxy-a05-64gb-and-4gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A05 128GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32444/mobile/aamsung-galaxy-a05-128gb-and-4gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A05s 128GB / 6GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32177/mobile/samsung-galaxy-a05s-128gb-and-6gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A05 128GB / 6GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32176/mobile/aamsung-galaxy-a05-128gb-and-6gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A05s 64GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32446/mobile/samsung-galaxy-a05s-64gb-and-4gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A05s 128GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32445/mobile/samsung-galaxy-a05s-128gb-and-4gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A06 128GB / 4GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001019692",
            "farnaa": "https://farnaa.com/product/43083/mobile/samsung-galaxy-a06-128gb-and-4gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010069002/Mobile-Samsung-A06-(4GB-128GB-4G)-China",
            "technobusiness": "https://www.technolifeb2b.com/product-57996/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a06-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-4-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a06-4g-1284gb"
        }
    },
    {
        "model": "Galaxy A06 128GB / 6GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001020901",
            "farnaa": "https://farnaa.com/product/43027/mobile/samsung-galaxy-a06-128gb-and-6gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010069003/Mobile-Samsung-A06-(6GB-128GB-4G)-China",
            "technobusiness": "https://www.technolifeb2b.com/product-58573/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a06-4g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-6-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a06-4g-1286gb"
        }
    },
    {
        "model": "Galaxy A25 5G 128GB / 6GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013531",
            "farnaa": "https://farnaa.com/product/32519/mobile/samsung-galaxy-a25-128gb-and-6gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010064003/Mobile-Samsung-A25-(6GB-128GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-32539/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a25-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-6-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a25-5g-1286gb"
        }
    },
    {
        "model": "Galaxy A25 5G 256 GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001015918",
            "farnaa": "https://farnaa.com/product/32472/mobile/samsung-galaxy-a25-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010064004/Mobile-Samsung-A25-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-32034/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a25-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a25-5g-2568gb"
        }
    },
    {
        "model": "Galaxy A26 5G 128 GB / 6GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://aasood.com/product/2000010019009001/Mobile-Samsung-A26-(6GB-128GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a26-5g-1286gb"
        }
    },
    {
        "model": "Galaxy A26 5G 256 GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://aasood.com/product/2000010019009002/Mobile-Samsung-A26-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a26-5g-2568gb"
        }
    },
    {
        "model": "Galaxy A35 5G 128GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014448",
            "farnaa": "https://farnaa.com/product/42609/mobile/samsung-galaxy-a35-5g-128gb-and-8gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010067002/Mobile-Samsung-A35-(8GB-128GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-35828/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a35-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A35 5G 256GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014467",
            "farnaa": "https://farnaa.com/product/42604/mobile/samsung-galaxy-a35-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010067001/Mobile-Samsung-A35-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-31018/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-a35-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a35-5g-2568gb"
        }
    },
    {
        "model": "Galaxy A55 5G 128GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014615",
            "farnaa": "https://farnaa.com/product/42610/mobile/samsung-galaxy-a55-5g-128gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010068002/Mobile-Samsung-A55-(8GB-128GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-35830/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%DA%AF%D9%84%DA%A9%D8%B3%DB%8C-a55-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-128-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy A55 5G 256GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014466",
            "farnaa": "https://farnaa.com/product/42574/mobile/samsung-galaxy-a55-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010068001/Mobile-Samsung-A55-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-31023/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%DA%AF%D9%84%DA%A9%D8%B3%DB%8C-a55-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy S23 FE 5G 256GB / 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014421",
            "farnaa": "https://farnaa.com/product/42676/mobile/samsung-galaxy-s23-fe-5g-256gb-and-8gb-ram-mobile-phone-vietnam-pack",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/product-29290/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-s23-fe-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-s23-fe-5g-2568gb"
        }
    },
    {
        "model": "Galaxy S24 Ultra 5G 256GB / 12GB Vietnam ",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013512",
            "farnaa": "https://farnaa.com/product/32535/mobile/samsung-galaxy-s24-ultra-5g-256gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010010065001/Mobile-Samsung-S24-Ultra-(12GB-256GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-33617/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%DB%8C%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-galaxy-s24-ultra-5g-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-12-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-s24-ultra-25612gb"
        }
    },
    {
        "model": "Galaxy S25 Ultra 5G 256GB / 12GB Vietnam ",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/galaxy-s25-ultra-5g-256gb-ram-12gb-vietnam",
            "farnaa": "https://farnaa.com/product/43324/mobile/samsung-galaxy-s25-ultra-5g-256gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010019006124/Mobile-Samsung-S25-Ultra-(12GB-256GB-5G)-Vietnam",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-s25-ultra-25612gb"
        }
    },
    {
        "model": "Galaxy S24 FE 5G 256GB RAM 8GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001020770",
            "farnaa": "https://farnaa.com/product/43117/mobile/samsung-galaxy-s24-fe-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010010070001/Mobile-Samsung-S24-FE-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "https://www.technolifeb2b.com/product-61669/%DA%AF%D9%88%D8%B4%DB%8C-%D9%85%D9%88%D8%A8%D8%A7%D9%8A%D9%84-%D8%B3%D8%A7%D9%85%D8%B3%D9%88%D9%86%DA%AF-%D9%85%D8%AF%D9%84-galaxy-s24-fe-%D8%B8%D8%B1%D9%81%DB%8C%D8%AA-256-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA-%D8%B1%D9%85-8-%DA%AF%DB%8C%DA%AF%D8%A7%D8%A8%D8%A7%DB%8C%D8%AA---%D9%88%DB%8C%D8%AA%D9%86%D8%A7%D9%85",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-s24-fe-2568gb"
        }
    },
    {
        "model": "apple series 9 aluminum 45mm smart watch",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/product/lpd-11704/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D8%A7%D9%BE%D9%84-%D9%85%D8%AF%D9%84-apple-watch-series-9-aluminum-case-45mm-%D8%A8%D8%A7-%DA%AF%D8%A7%D8%B1%D8%A7%D9%86%D8%AA%DB%8C-18-%D9%85%D8%A7%D9%87-%D8%B4%D8%B1%DA%A9%D8%AA%DB%8C",
            "farnaa": "https://farnaa.com/product/32301/wristband-and-smart-watch/apple-series-9-aluminum-45mm-smart-watch",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "apple series 9 aluminum 41mm smart watch",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/product/lpd-11709/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D8%A7%D9%BE%D9%84-%D9%85%D8%AF%D9%84-apple-watch-series-9-aluminum-case-41mm-%D8%A8%D8%A7-%DA%AF%D8%A7%D8%B1%D8%A7%D9%86%D8%AA%DB%8C-18-%D9%85%D8%A7%D9%87-%D8%B4%D8%B1%DA%A9%D8%AA%DB%8C",
            "farnaa": "https://farnaa.com/product/32300/wristband-and-smart-watch/apple-series-9-aluminum-41mm-smart-watch",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "apple watch se gen2 2023 44mm aluminum silicone sport band",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/product/lpd-20528/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D8%A7%D9%BE%D9%84-%D9%85%D8%AF%D9%84-apple-watch-series-se-2023-aluminum-case-sport-loop-44mm-%D8%A8%D8%A7-%DA%AF%D8%A7%D8%B1%D8%A7%D9%86%D8%AA%DB%8C-18-%D9%85%D8%A7%D9%87%D9%87-%D8%B4%D8%B1%DA%A9%D8%AA%DB%8C",
            "farnaa": "https://farnaa.com/product/42575/wristband-and-smart-watch/apple-watch-se-gen2-2023-44mm-aluminum-silicone-sport-band",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "AirPods 4-ANC",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/product/lpd-20002/%D9%87%D8%AF%D9%81%D9%88%D9%86-%D8%A8%DB%8C-%D8%B3%DB%8C%D9%85-%D8%A7%D9%BE%D9%84-%D9%85%D8%AF%D9%84-airpods-4-anc-%D8%A8%D8%A7-%DA%AF%D8%A7%D8%B1%D8%A7%D9%86%D8%AA%DB%8C-18%D9%85%D8%A7%D9%87%D9%87-%D8%B4%D8%B1%DA%A9%D8%AA%DB%8C",
            "farnaa": "https://farnaa.com/product/43111/handsfree/apple-airpods-4-anc-wireless-headphones",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "apple watch se gen2 2023 40mm aluminum silicone sport band",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/product/lpd-11812/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D8%A7%D9%BE%D9%84-%D9%85%D8%AF%D9%84-apple-watch-series-se-2023-aluminum-case-40mm-%D8%A8%D8%A7-%DA%AF%D8%A7%D8%B1%D8%A7%D9%86%D8%AA%DB%8C-18-%D9%85%D8%A7%D9%87-%D8%B4%D8%B1%DA%A9%D8%AA%DB%8C",
            "farnaa": "https://farnaa.com/product/42573/wristband-and-smart-watch/apple-watch-se-gen2-2023-40mm-aluminum-silicone-sport-band",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "POCO M6 Pro 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013597",
            "farnaa": "https://farnaa.com/product/32563/mobile/xiaomi-poco-m6-pro-4g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Redmi Note 13 Pro 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013864",
            "farnaa": "https://farnaa.com/product/32562/mobile/xiaomi-redmi-note-13-pro-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020068003/Mobile-Xiaomi-Redmi-Note-13-Pro-(12GB-512GB-5G)-Global",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Redmi Note 13 Pro 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013657",
            "farnaa": "https://farnaa.com/product/32171/mobile/xiaomi-redmi-note-13-pro-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Redmi Note 13 256GB RAM 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001014939",
            "farnaa": "https://farnaa.com/product/32479/mobile/xiaomi-redmi-note-13-5g-256gb-and-8gb-ram-mobile-phone-global-pack",
            "aasood": "https://aasood.com/product/2000010020069002/Mobile-Xiaomi-Redmi-Note-13-(8GB-256GB-4G)-Global",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Redmi 13 256GB RAM 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001019706",
            "farnaa": "https://farnaa.com/product/42794/mobile/xiaomi-redmi13-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Poco C75 256GB RAM 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001020960",
            "farnaa": "https://farnaa.com/product/43171/mobile/xiaomi-poco-c75-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-c75-4g-2568gb"
        }
    },
    {
        "model": "Redmi Note 13 Pro Plus 5G 512GB RAM 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013723",
            "farnaa": "https://farnaa.com/product/32174/mobile/xiaomi-redmi-note-13-pro-plus-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "POCO X6 PRO 5G 512GB RAM 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013518",
            "farnaa": "https://farnaa.com/product/32557/mobile/xiaomi-poco-x6-pro-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-x6-pro-5g-256gb12gb"
        }
    },
    {
        "model": "POCO M6 Pro 4G 256GB RAM 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001013917",
            "farnaa": "https://farnaa.com/product/32560/mobile/xiaomi-poco-m6-pro-4g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product-list/2220",
            "technobusiness": "https://www.technolifeb2b.com/pro%D8%A7",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy Tab A9 (X115) 4G 64/4",
        "category": "Tablet Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32513/tablet/samsung-galaxy-tab-a9-x115-4g-64gb-and-4gb-ram-tablet",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy Tab S9 X716 5G 256/12",
        "category": "Tablet Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/32451/tablet/samsung-galaxy-tab-s9-5g-256gb-and-12gb-ram-tablet",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy Tab A9+ X216 5G 64/4",
        "category": "Tablet Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://m.aasood.com/product/2000020010015002/Tablet-Samsung-Galaxy-Tab-A9+-(X216)-(4GB-64GB-5G)-China",
            "technobusiness": "",
            "kasrapars": ""
            
        }
    },
        {
        "model": "Galaxy Tab S9 Fe Plus X616b 256/12",
        "category": "Tablet Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://aasood.com/product/2000020010016001/Tablet-Samsung-Galaxy-Tab-S9-Fe-+(X616b)-(12GB-256GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "iPhone 16 Pro Max Not 256 GB ZAA",
        "category": "Apple",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/iphone-16-pro-max-256gb-zaa-non-active",
            "farnaa": "https://farnaa.com/product/43186/mobile/apple-iphone-16promax-not-active-dual-sim-256gb-and-ram-8gb-mobile-phone",
            "aasood": "https://aasood.com/product/2000010040008001/Mobile-Apple-iPhone-16-Pro-Max-Not-Active-(8GB-256GB-5G)-ZA/A",
            "technobusiness": "",
            "kasrapars": ""
        }
        },
        {
        "model": "iPhone 16 Pro Max Not 512 GB ZAA",
        "category": "Apple",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/apple-iphone-16-pro-max-5128gb"
        },
        "custom_color_map": {
            "Natural Titanium": "Natural Titanium",
            "Desert Titanium": "Desert Titanium",
            "Black Titanium": "Black Titanium",
            "White Titanium": "White Titanium",
            "تیتانیوم - طبیعی": "Natural Titanium",
            "تیتانیوم - سفید": "White Titanium",
            "تیتانیوم - صحرایی": "Desert Titanium",
            "تیتانیوم - مشکی": "Black Titanium",
            "مشکی": "Black Titanium",
            "دیزرت": "Desert Titanium",
            "سفید": "White Titanium",
            "نچرال": "Natural Titanium",
            
            # سایر نگاشت‌های اختصاصی برای این محصول
        }
    },
    {
        "model": "iPhone 16 Pro Not 256 GB ZAA",
        "category": "Apple",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/iphone-16-pro-256gb-zaa-non-active",
            "farnaa": "https://farnaa.com/product/43189/mobile/apple-iphone-16pro-not-active-dual-sim-256gb-and-ram-8gb-mobile-phone",
            "aasood": "https://aasood.com/product/2000010040007001/Mobile-Apple-iPhone-16-Pro-Not-Active-(8GB-256GB-5G)-ZA/A",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/apple-iphone-16-pro-2568gb"
        },
        "custom_color_map": {
            "Natural Titanium": "Natural Titanium",
            "Desert Titanium": "Desert Titanium",
            "Black Titanium": "Black Titanium",
            "White Titanium": "White Titanium",
            "تیتانیوم - طبیعی": "Natural Titanium",
            "تیتانیوم - سفید": "White Titanium",
            "تیتانیوم - صحرایی": "Desert Titanium",
            "تیتانیوم - مشکی": "Black Titanium",
            "مشکی": "Black Titanium",
            "دیزرت": "Desert Titanium",
            "سفید": "White Titanium",
            "نچرال": "Natural Titanium",
            
            # سایر نگاشت‌های اختصاصی برای این محصول
        }
    },
    {
        "model": "iPhone 16 Not 128 GB CH",
        "category": "Apple",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/iphone-16-128gb-cha-non-active",
            "farnaa": "https://farnaa.com/product/43194/mobile/apple-iphone-16-not-active-dual-sim-128gb-and-ram-8gb-mobile-phone",
            "aasood": "https://aasood.com/product/2000010040009002/Mobile-Apple-iPhone-16-Not-Active-(8GB-128GB-5G)-CH",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/apple-iphone-16-1288gb"
        },
    },
    {
        "model": "iPhone 16 Not 256 GB CH",
        "category": "Apple",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/iphone-16-256gb-cha-non-active",
            "farnaa": "https://farnaa.com/product/43193/mobile/apple-iphone-16-not-active-dual-sim-256gb-and-ram-8gb-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/apple-iphone-16-2568gb"
        },
    },
    {
        "model": "Galaxy A56 128GB / 8GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43539/mobile/samsung-galaxy-a56-5g-128gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010019008001/Mobile-Samsung-A56-(8GB-128GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a56-5g-1288gb"
        },
    },
    {
        "model": "Galaxy A56 256GB / 8GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43540/mobile/samsung-galaxy-a56-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010019008002/Mobile-Samsung-A56-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a56-5g-2568gb"
        },
    },
    {
        "model": "Galaxy A56 256GB / 12GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://aasood.com/product/2000010019008003/Mobile-Samsung-A56-(12GB-256GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a56-5g-25612gb"
        },
    },
    {
        "model": "Galaxy A36 128GB / 8GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43535/mobile/samsung-galaxy-a36-5g-128gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010019007001/Mobile-Samsung-A36-(8GB-128GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a36-5g-1288gb"
        },
    },
    {
        "model": "Galaxy A36 256GB / 8GB",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43537/mobile/samsung-galaxy-a36-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010019007002/Mobile-Samsung-A36-(8GB-256GB-5G)-Vietnam",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/samsung-galaxy-a36-5g-2568gb"
        },
    },
    {
        "model": "Apple AirPods 3",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/30561/handsfree/apple-airpods-3-wireless-headphones",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "apple airpods 4",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-wireless-airpods-4-wireless-headphones-with-18-month-corporate-warranty",
            "farnaa": "https://farnaa.com/product/43110/handsfree/apple-airpods-4-wireless-headphones",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "apple airpods pro 2nd generation 2023",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-bluetooth-headphones-airpods-pro-2nd-generation-new-usbc-with-18-month-corporate-warranty",
            "farnaa": "https://farnaa.com/product/32420/handsfree/apple-airpods-pro-2nd-generation-2023-bluetooth-earbuds",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple AirPods 2",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/10125/handsfree/apple-airpods-2-wireless-headphones",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "samsung galaxy buds 3",
        "category": "Samsung Acc",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43059/handsfree/samsung-galaxy-buds-3-wireless-headphone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple Watch Series 10 Aluminium Case 42mm",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-10-series-apple-watch-series-10-aluminium-case-42mm-with-an-18-month-corporate-warranty",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple Watch Series10 Aluminium Case 46mm",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-10-series-apple-watch-series10-aluminium-case-46mm-with-an-18-month-corporate-warranty",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple Watch Series Se 2024 Aluminium Case 44mm",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-watch-apple-watch-series-se-2024-aluminium-case-44mm-with-an-18-month-corporate-warranty",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple Watch Series 10 Aluminum Case 42mm Sport Loop",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/apple-watch-apple-watch-series-10-aluminum-case-42mm-sport-loop-with-an-18-month-corporate-warranty",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "SAMSUNG Galaxy Watch 7 L300 - 40mm",
        "category": "Samsung Acc",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/1001019508",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Apple Series 10 46mm Aluminum Silicone Sport Band",
        "category": "Apple Acc",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "https://aasood.com/product/2100100080010001/%D8%B3%D8%A7%D8%B9%D8%AA-%D9%87%D9%88%D8%B4%D9%85%D9%86%D8%AF-%D8%A7%D9%BE%D9%84-%D8%B3%D8%B1%DB%8C-10-%D8%B3%D8%A7%DB%8C%D8%B2-46-%D8%A8%D8%A7%D8%A8%D9%86%D8%AF-%D8%B3%DB%8C%D9%84%DB%8C%DA%A9%D9%88%D9%86%DB%8C-%D9%85%D8%AF%D9%84--Apple-Series-10-46mm-Aluminum-Silicone-Sport-Band",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy S25 Plus 5G 256GB / 12GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "https://hamrahtel.com/products/galaxy-s25plus-5g-256gb-ram-12gb-vietnam",
            "farnaa": "https://farnaa.com/product/43400/mobile/samsung-galaxy-s25-plus-5g-256gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy S25 5G 128GB / 12GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43403/mobile/samsung-galaxy-s25-5g-128gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy S25 5G 256GB / 12GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43402/mobile/samsung-galaxy-s25-5g-256gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Galaxy S25 5G 512GB / 12GB Vietnam",
        "category": "Samsung",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43401/mobile/samsung-galaxy-s25-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": ""
        }
    },
    {
        "model": "Xiaomi 14T Pro 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43092/mobile/xiaomi-14t-pro-512gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-14t-pro-51212gb"
        }
    },
    {
        "model": "Xiaomi 14T 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43100/mobile/xiaomi-14t-512gb-and-12gb-ram-mobile-phone",
            "aasood": "http://aasood.com/product/2000010020078002/Mobile-Xiaomi-14T-(12GB-512GB-5G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-14t-51212gb"
        }
    },
    {
        "model": "Xiaomi 13T Pro 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-13t-pro-5g-51212gb"
        }
    },
    {
        "model": "Poco X7 Pro 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43385/mobile/xiaomi-poco-x7pro-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/x7-pro-51212gb"
        }
    },
    {
        "model": "Xiaomi Redmi Note 14 Pro Plus 5G 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43453/mobile/xiaomi-redmi-note-14-pro-plus-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020083001/Mobile-Xiaomi-Redmi-Note-14-Pro+-(12GB-512GB-5G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14-pro-plus-5g-51212gb"
        }
    },
    {
        "model": "Poco X7 Pro 256GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43386/mobile/xiaomi-poco-x7pro-5g-256gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-x7-pro-25612gb"
        }
    },
    {
        "model": "Poco X7 Pro 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43387/mobile/xiaomi-poco-x7pro-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-x7-pro-2568gb"
        }
    },
    {
        "model": "Poco F5 256GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-f5-25612gb"
        }
    },
    {
        "model": "Redmi Note 14 Pro 5G 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43141/mobile/xiaomi-redmi-note-14-pro-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020082003/Mobile-Xiaomi-Redmi-Note-14-Pro-(12GB-512GB-5G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14-pro-5g-51212gb"
        }
    },
    {
        "model": "Redmi Note 14 Pro 4G 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43384/mobile/xiaomi-redmi-note-14-pro-4g-dual-sim-512gb-and-12gb-global-pack-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14-pro-4g-51212gb"
        }
    },
    {
        "model": "Poco X7 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43372/mobile/xiaomi-poco-x7-5g-256gb-and-8gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-x7-2568gb"
        }
    },
    {
        "model": "Poco X7 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43370/mobile/xiaomi-poco-x7-5g-512gb-and-12gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-x7-51212gb"
        }
    },
    {
        "model": "Redmi Note 14S 512GB / 12GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43593/mobile/xiaomi-redmi-note-14s-512-gb-and-ram-12-gb-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020085001/Mobile-Xiaomi-Redmi-Note-14S-(8GB-256GB-4G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14s-4g-51212gb"
        }
    },
    {
        "model": "Redmi Note 14S 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43592/mobile/xiaomi-redmi-note-14s-256-gb-and-ram-8-gb-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14s-4g-2568gb"
        }
    },
    {
        "model": "Redmi Note 14 Pro 4G 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43382/mobile/xiaomi-redmi-note-14-pro-4g-dual-sim-256gb-and-8gb-global-pack-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14-pro-4g-2568gb"
        }
    },
    {
        "model": "Redmi Note 14 4G 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43380/mobile/xiaomi-redmi-note-14-4g-dual-sim-256gb-and-8gb-global-pack-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-note-14-4g-2568gb"
        }
    },
    {
        "model": "Poco M5s 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/poco-m5s-2568gb-ram-2207117bpg"
        }
    },
    {
        "model": "Redmi 14C 4G 256GB / 8GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43082/mobile/xiaomi-14c-256gb-and-8gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020077001/Mobile-Xiaomi-Redmi-14C-(8GB-256GB-4G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-14c-4g-2568gb"
        }
    },
    {
        "model": "Redmi 14C 4G 128GB / 6GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43079/mobile/xiaomi-14c-128gb-and-6gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-14c-4g-1286gb"
        }
    },
    {
        "model": "Redmi 14C 4G 128GB / 4GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43078/mobile/xiaomi-14c-128gb-and-4gb-ram-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020077002/Mobile-Xiaomi-Redmi-14C-(4GB-128GB-4G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-14c-4g-128-4gb"
        }
    },
    {
        "model": "Redmi A3X 128GB / 4GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43056/mobile/xiaomi-redmi-a3x-128gb-and-4gb-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-a3x-1284gb"
        }
    },
    {
        "model": "Redmi A3X 64GB / 3GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43170/mobile/xiaomi-redmi-a3x-64gb-and-3gb-mobile-phone",
            "aasood": "https://aasood.com/product/2000010020075002/Mobile-Xiaomi-Redmi-A3X-(3GB-64GB-4G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-a3x-643gb"
        }
    },
    {
        "model": "Redmi A5 4G 128GB / 4GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43582/mobile/xiaomi-redmi-a5-4g-128gb-and-4gb-ram-mobile-phone",
            "aasood": "",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-a5-4g-1284gb"
        }
    },
    {
        "model": "Redmi A5 4G 64GB / 3GB",
        "category": "Xiaomi",
        "urls": {
            "hamrahtel": "",
            "farnaa": "https://farnaa.com/product/43580/mobile/xiaomi-redmi-a5-4g-64gb-and-3gb-ram-mobile-phone",
            "aasood": "https://m.aasood.com/product/2000010020084002/Mobile-Xiaomi-Redmi-A5-(3GB-64GB-4G)-Global",
            "technobusiness": "",
            "kasrapars": "https://plus.kasrapars.ir/product/xiaomi-redmi-a5-4g-643gb"
        }
    },

        # اگر محصول دیگری هم دارید اضافه کنید
    ]

    # تعیین تعداد پراسس
    num_processes = 25  # با توجه به منابع سیستم قابل تغییر است

    product_chunks = list(chunkify(products_info, num_processes))
    total_chunks = len(product_chunks)    # تعداد چانک
    total_products = len(products_info)   # تعداد کل محصولات

    all_results = []

    # -- متغیرهایی برای محاسبه و چاپ درصد به شکل گسسته (5%، 10%، 15% و ...)
    completed_products = 0
    next_print_threshold = 5  # آستانهٔ اول برای چاپ درصد

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        # هر چانک را همراه با اندیس آن ارسال می‌کنیم
        futures = {
            executor.submit(scrape_chunk, chunk, idx + 1, total_chunks, total_products): chunk
            for idx, chunk in enumerate(product_chunks)
        }

        for future in concurrent.futures.as_completed(futures):
            # چانک اصلی مرتبط با این future:
            chunk = futures[future]
            try:
                chunk_result = future.result()
                all_results.extend(chunk_result)
            except Exception as e:
                print(f"Error in processing chunk: {e}")

            # تعداد محصولات تکمیل‌شده بعد از این چانک
            completed_products += len(chunk)

            # محاسبهٔ درصد پیشرفت کل
            overall_progress = (completed_products / total_products) * 100

            # چاپ درصد در گام‌های 5 درصدی
            while overall_progress >= next_print_threshold and next_print_threshold <= 100:
                print(f"{next_print_threshold}%")
                next_print_threshold += 5

    # بخش دهم: تبدیل نتایج به DataFrame، ذخیره در دیتابیس و ذخیره در اکسل

    df = pd.DataFrame(all_results)

    if not df.empty:
        df['1%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.03, -4))))
        df['2%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.04, -4))))
        df['3%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.05, -4))))
        df['4%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.06, -4))))
        df['4.5%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.065, -4))))
        df['5%'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.07, -4))))
        df['رست این'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.015, -4))))
        df['داریک'] = df['کمترین قیمت'].apply(lambda x: "{:,}".format(int(round(int(x.replace(',', '')) * 1.115, -4))))

    if not df.empty:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            model TEXT,
            category TEXT,
            color TEXT,
            hamrahtel_price TEXT,
            farnaa_price TEXT,
            aasood_price TEXT,
            technobusiness_price TEXT,
            kasrapars_price TEXT,
            min_price TEXT,
            date TEXT,
            percent_1 TEXT,
            percent_2 TEXT,
            percent_3 TEXT,
            percent_4 TEXT,
            percent_4_5 TEXT,
            percent_5 TEXT,
            rest_in TEXT,
            tap30 TEXT
        )
        ''')

        for _, row in df.iterrows():
            cursor.execute('''
            INSERT INTO products (
                model, category, color,
                hamrahtel_price, farnaa_price, aasood_price, technobusiness_price, kasrapars_price,
                min_price, date,
                percent_1, percent_2, percent_3, percent_4, percent_4_5, percent_5, rest_in, tap30
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['مدل'],
                row['دسته‌بندی'],
                row['رنگ'],
                row.get('قیمت همراه‌تل', "0"),
                row.get('قیمت فرنا', "0"),
                row.get('قیمت آسوود', "0"),
                row.get('قیمت تکنو بیزینس', "0"),
                row.get('قیمت کسری پارس', "0"),
                row['کمترین قیمت'],
                row['تاریخ'],
                row.get('1%', "0"),
                row.get('2%', "0"),
                row.get('3%', "0"),
                row.get('4%', "0"),
                row.get('4.5%', "0"),
                row.get('5%', "0"),
                row.get('داریک', "0"),
                row.get('تپسی', "0")
            ))
        conn.commit()
        conn.close()

    if not df.empty:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            categories = df['دسته‌بندی'].unique()
            for cat in categories:
                df_cat = df[df['دسته‌بندی'] == cat]
                df_cat.to_excel(writer, sheet_name=cat, index=False)

    print(f"\n\033[95mProcess finished.\033[0m Total rows: {len(df)}")
    print(f"Database saved in: {db_name}")
    print(f"Excel file saved at: {file_path}")
