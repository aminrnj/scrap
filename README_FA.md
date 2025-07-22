# ربات ردیابی قیمت محصولات

یک اپلیکیشن وب Flask برای ردیابی قیمت محصولات از سایت‌های مختلف فروشگاهی در ایران. این اپلیکیشن قابلیت‌های نظارت بر قیمت، مدیریت کاربران و سیستم تیکت را فراهم می‌کند.

## ویژگی‌ها

- **ردیابی قیمت**: نظارت بر قیمت محصولات از سایت‌های مختلف فروشگاهی
- **مدیریت کاربران**: پنل ادمین برای ثبت‌نام و مدیریت کاربران
- **سیستم تیکت**: سیستم پشتیبانی برای درخواست‌های کاربران
- **درخواست اسکرپ**: کاربران می‌توانند محصولات جدید برای اسکرپ درخواست دهند
- **خروجی اکسل**: دانلود داده‌های قیمت در فرمت اکسل
- **تقویم فارسی**: پشتیبانی از تقویم شمسی (جلالی)
- **به‌روزرسانی زنده**: به‌روزرسانی زنده قیمت‌ها و اعلان‌ها

## تکنولوژی‌های استفاده شده

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **دیتابیس**: SQLite
- **وب اسکرپینگ**: Selenium, BeautifulSoup
- **احراز هویت**: Flask-Login
- **مدیریت تاریخ**: jdatetime, pytz

## نصب و راه‌اندازی

### 1. کلون کردن repository
```bash
git clone https://github.com/aminrnj/scrap.git
cd scrap
```

### 2. ایجاد محیط مجازی
```bash
python -m venv venv
```

### 3. فعال‌سازی محیط مجازی
- Windows:
  ```bash
  venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

### 4. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 5. ایجاد فایل‌های پیکربندی مورد نیاز

#### فایل `authorized_users.json`
```json
{
  "admin": {
    "username": "admin",
    "password": "your_admin_password",
    "can_update": true,
    "can_download_excel": true,
    "can_request_scrap": true,
    "can_view_predefined_percent": true,
    "can_use_custom_percent": true
  }
}
```

#### فایل `users.json`
```json
{
  "users": [
    {
      "username": "user1",
      "password": "user1_password",
      "can_update": false,
      "can_download_excel": true,
      "can_request_scrap": true,
      "can_view_predefined_percent": true,
      "can_use_custom_percent": false
    }
  ]
}
```

#### فایل `update_lock.json`
```json
{
  "locked": false,
  "last_update": null,
  "update_in_progress": false
}
```

### 6. دانلود ChromeDriver

1. به سایت [ChromeDriver](https://chromedriver.chromium.org/) بروید
2. نسخه مناسب با Chrome خود را دانلود کنید
3. فایل‌ها را در پوشه `chromedriver-win64/` قرار دهید

### 7. راه‌اندازی دیتابیس
```bash
python migrate.py
```

### 8. اجرای اپلیکیشن
```bash
python app.py
```

## ساختار پروژه

```
scrap/
├── app.py                 # اپلیکیشن اصلی Flask
├── bot.py                 # ربات تلگرام
├── scrap.py              # عملکرد وب اسکرپینگ
├── requirements.txt       # وابستگی‌های Python
├── templates/            # قالب‌های HTML
├── static/              # فایل‌های CSS، JS و استاتیک
├── migrations/          # migration های دیتابیس
├── db/                  # فایل‌های دیتابیس
└── instance/            # فایل‌های مخصوص instance
```

## نقاط پایانی API

- `GET /` - داشبورد اصلی
- `GET /login` - صفحه ورود
- `POST /login` - احراز هویت ورود
- `GET /api/products` - دریافت داده‌های محصول
- `POST /update` - به‌روزرسانی داده‌های محصول
- `GET /api/product-history/<model>` - تاریخچه قیمت محصول
- `GET /api/weekly-stats` - آمار هفتگی
- `GET /api/dollar-price` - داده‌های قیمت دلار
- `POST /scrap-request` - ارسال درخواست اسکرپ
- `GET /view-requests` - مشاهده درخواست‌های اسکرپ
- `POST /ticket` - ارسال تیکت پشتیبانی
- `GET /view-tickets` - مشاهده تیکت‌ها

## مدل‌های دیتابیس

- **User**: حساب‌های کاربری و مجوزها
- **ScrapRequest**: درخواست‌های اسکرپ کاربران
- **Ticket**: تیکت‌های پشتیبانی و پاسخ‌ها

## نحوه استفاده

1. **دسترسی به اپلیکیشن**: به آدرس `http://localhost:5000` بروید
2. **ورود**: از اطلاعات ادمین برای دسترسی به داشبورد استفاده کنید
3. **نظارت بر قیمت‌ها**: داده‌های قیمت زنده برای محصولات ردیابی شده را مشاهده کنید
4. **مدیریت کاربران**: از طریق پنل ادمین مجوزهای کاربران را اضافه/ویرایش کنید
5. **مدیریت تیکت‌ها**: به درخواست‌های پشتیبانی کاربران پاسخ دهید

## فایل‌های مهم که باید اضافه شوند

### 1. فایل‌های پیکربندی
این فایل‌ها برای امنیت در `.gitignore` قرار گرفته‌اند و باید به صورت دستی ایجاد شوند:

#### `authorized_users.json`
```json
{
  "admin": {
    "username": "admin",
    "password": "your_secure_password_here",
    "can_update": true,
    "can_download_excel": true,
    "can_request_scrap": true,
    "can_view_predefined_percent": true,
    "can_use_custom_percent": true
  }
}
```

#### `users.json`
```json
{
  "users": [
    {
      "username": "user1",
      "password": "user1_password",
      "can_update": false,
      "can_download_excel": true,
      "can_request_scrap": true,
      "can_view_predefined_percent": true,
      "can_use_custom_percent": false
    }
  ]
}
```

#### `update_lock.json`
```json
{
  "locked": false,
  "last_update": null,
  "update_in_progress": false
}
```

### 2. ChromeDriver
1. به [سایت ChromeDriver](https://chromedriver.chromium.org/) بروید
2. نسخه مناسب با Chrome خود را دانلود کنید
3. فایل‌ها را در پوشه `chromedriver-win64/` قرار دهید

### 3. فایل‌های دیتابیس
پوشه `instance/` و `db/` به صورت خودکار ایجاد می‌شوند.

## نکات امنیتی

- کلید `SECRET_KEY` پیش‌فرض را در محیط تولید تغییر دهید
- از متغیرهای محیطی برای تنظیمات حساس استفاده کنید
- وابستگی‌ها را به طور منظم به‌روزرسانی کنید
- احراز هویت و مجوزدهی مناسب را پیاده‌سازی کنید

## عیب‌یابی

### مشکل: ChromeDriver پیدا نمی‌شود
**راه حل**: مطمئن شوید که ChromeDriver در پوشه `chromedriver-win64/` قرار دارد.

### مشکل: خطای دیتابیس
**راه حل**: فایل `migrate.py` را اجرا کنید:
```bash
python migrate.py
```

### مشکل: خطای import
**راه حل**: مطمئن شوید که محیط مجازی فعال است و وابستگی‌ها نصب شده‌اند:
```bash
pip install -r requirements.txt
```

## پشتیبانی

برای پشتیبانی و سوالات، لطفاً یک issue در repository GitHub ایجاد کنید یا با تیم توسعه تماس بگیرید.

## مشارکت

1. پروژه را fork کنید
2. یک شاخه feature ایجاد کنید
3. تغییرات خود را اعمال کنید
4. یک pull request ارسال کنید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. 