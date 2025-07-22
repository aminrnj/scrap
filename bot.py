from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
from datetime import datetime
import os
import subprocess
import json
import sqlite3
from sqlalchemy import create_engine, text
import time

TOKEN = "7634348306:AAHTG2-HAtKt9hl_q8yFZlgncdM4DcA_iA4"
ADMIN_CHAT_ID = '2821814'
CHANNEL_CHAT_ID = '@Dollardata'

# مسیر دیتابیس
DATABASE_PATH = r"C:\inetpub\wwwroot\flask v0.3\datasitenews5.db"

# مسیر فایل اکسل
EXCEL_FILE_PATH = r"C:\inetpub\wwwroot\flask v0.3\static\scrap.xlsx"

# مسیر فایل ذخیره‌سازی کاربران مجاز
AUTHORIZED_USERS_FILE = "authorized_users.json"

# مسیر فایل ذخیره‌سازی کاربران
USERS_FILE = "users.json"

# حالت‌های ربات
SEARCHING = 'searching'
SELECTING_PRODUCT = 'selecting_product'

UPDATE_LOCK_FILE = "update_lock.json"
UPDATE_COOLDOWN_SECONDS = 3600  # 1 hour

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as f:
            return json.load(f)
    return [ADMIN_CHAT_ID]  # ادمین همیشه دسترسی دارد

def save_authorized_users(users):
    with open(AUTHORIZED_USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_update_lock():
    if os.path.exists(UPDATE_LOCK_FILE):
        with open(UPDATE_LOCK_FILE, 'r') as f:
            return json.load(f)
    return {"locked": False, "last_update": 0}

def save_update_lock(lock_data):
    with open(UPDATE_LOCK_FILE, 'w') as f:
        json.dump(lock_data, f)

# ایجاد کیبورد دائمی
def get_keyboard():
    keyboard = [
        [KeyboardButton("🔄 شروع بروزرسانی"), KeyboardButton("⏰ آخرین بروزرسانی")],
        [KeyboardButton("📊 دریافت فایل اکسل"), KeyboardButton("🔍 جستجوی محصول")],
        [KeyboardButton("ℹ️ درباره ربات")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# تابع دریافت لیست محصولات از دیتابیس
async def get_products_list(search_query: str = None) -> list:
    try:
        engine = create_engine(f"sqlite:///{DATABASE_PATH}")
        if search_query:
            query = text("""
                SELECT 
                    model,
                    min_price,
                    hamrahtel_price,
                    farnaa_price,
                    aasood_price,
                    technobusiness_price,
                    kasrapars_price,
                    date,
                    category,
                    color
                FROM products
                WHERE date = (SELECT MAX(date) FROM products)
                  AND (LOWER(model) LIKE :search OR LOWER(category) LIKE :search)
                ORDER BY model
            """)
            params = {"search": f"%{search_query.lower()}%"}
        else:
            query = text("""
                SELECT 
                    model,
                    min_price,
                    hamrahtel_price,
                    farnaa_price,
                    aasood_price,
                    technobusiness_price,
                    kasrapars_price,
                    date,
                    category,
                    color
                FROM products
                WHERE date = (SELECT MAX(date) FROM products)
                ORDER BY model
            """)
            params = {}
        with engine.connect() as connection:
            result = connection.execute(query, params).mappings().all()
            
            # گروه‌بندی محصولات بر اساس مدل و حافظه
            products_by_model = {}
            for row in result:
                model = str(row['model'])
                
                # استخراج حجم حافظه از نام مدل
                storage = "نامشخص"
                if "GB" in model:
                    storage_parts = model.split("GB")
                    if len(storage_parts) > 1:
                        storage = storage_parts[0].strip().split()[-1] + "GB"
                
                # استخراج نام اصلی مدل (بدون حجم حافظه)
                base_model = model.replace(storage, "").strip()
                
                if base_model not in products_by_model:
                    products_by_model[base_model] = {
                        'name': base_model,
                        'category': row['category'],
                        'variants': {}
                    }
                
                if storage not in products_by_model[base_model]['variants']:
                    products_by_model[base_model]['variants'][storage] = {
                        'colors': {},
                        'min_price': float('inf')
                    }
                
                # تبدیل قیمت‌ها به عدد و حذف کاراکترهای غیر عددی
                def clean_price(price):
                    if not price:
                        return 0
                    try:
                        return int(''.join(filter(str.isdigit, str(price))))
                    except:
                        return 0
                
                # اضافه کردن رنگ و قیمت‌های آن
                color = row['color'] if row['color'] else "نامشخص"
                if color not in products_by_model[base_model]['variants'][storage]['colors']:
                    products_by_model[base_model]['variants'][storage]['colors'][color] = {
                        'hamrahtel': 0,
                        'farnaa': 0,
                        'aasood': 0,
                        'technobusiness': 0,
                        'kasrapars': 0
                    }
                
                # به‌روزرسانی قیمت‌های فروشگاه‌ها برای این رنگ
                for store in ['hamrahtel', 'farnaa', 'aasood', 'technobusiness', 'kasrapars']:
                    price = clean_price(row[f'{store}_price'])
                    if price > 0:
                        products_by_model[base_model]['variants'][storage]['colors'][color][store] = price
                        # به‌روزرسانی حداقل قیمت برای این مدل و حافظه
                        if price < products_by_model[base_model]['variants'][storage]['min_price']:
                            products_by_model[base_model]['variants'][storage]['min_price'] = price
            
            # تبدیل دیکشنری به لیست
            products = []
            for model, model_data in products_by_model.items():
                for storage, variant_data in model_data['variants'].items():
                    if variant_data['min_price'] != float('inf'):
                        product = {
                            'name': f"{model} - {storage}",
                            'category': model_data['category'],
                            'storage': storage,
                            'price': f"{variant_data['min_price']:,} تومان",
                            'colors': variant_data['colors']
                        }
                        products.append(product)
            
            return products
    except Exception as e:
        print(f"Error getting products from database: {e}")
        return []

# تابع ایجاد کیبورد اینلاین برای محصولات
def get_products_keyboard(products: list) -> InlineKeyboardMarkup:
    keyboard = []
    for i, product in enumerate(products):
        # هر دکمه حاوی نام محصول و قیمت آن است
        button_text = f"{product['name']} - {product['price']}"
        callback_data = f"product_{i}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # اضافه کردن دکمه بازگشت
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(keyboard)

# handler برای دکمه جستجو
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 لطفاً بخشی از مدل یا نام محصول را وارد کنید:")
    context.user_data['state'] = SEARCHING

# handler برای انتخاب محصول
async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_menu":
        context.user_data['state'] = None
        # حذف پیام اینلاین و ارسال پیام جدید با منوی اصلی
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.message.chat.send_message("منوی اصلی:", reply_markup=get_keyboard())
        return

    if query.data == "back_to_list":
        # برگشت به لیست محصولات
        products = context.user_data.get('products', [])
        if products:
            await query.message.edit_text(
                "📱 لطفاً محصول مورد نظر خود را انتخاب کنید:",
                reply_markup=get_products_keyboard(products)
            )
        else:
            await query.message.edit_text(
                "❌ هیچ محصولی یافت نشد.",
                reply_markup=get_keyboard()
            )
        return

    if query.data.startswith("product_"):
        product_index = int(query.data.split("_")[1])
        products = context.user_data.get('products', [])
        
        if 0 <= product_index < len(products):
            product = products[product_index]
            
            # ایجاد پیام با جزئیات قیمت‌ها
            message = f"""
📱 <b>اطلاعات محصول</b>

<b>نام:</b> {product['name']}
<b>دسته‌بندی:</b> {product['category']}

<b>رنگ‌ها و قیمت‌ها:</b>
"""
            # نمایش قیمت‌ها برای هر رنگ
            for color, prices in product['colors'].items():
                message += f"\n🎨 <b>{color}:</b>\n"
                if prices['hamrahtel']:
                    message += f"• همراه تل: {prices['hamrahtel']:,} تومان\n"
                if prices['farnaa']:
                    message += f"• فرناآ: {prices['farnaa']:,} تومان\n"
                if prices['aasood']:
                    message += f"• آسود: {prices['aasood']:,} تومان\n"
                if prices['technobusiness']:
                    message += f"• تکنوبیزنس: {prices['technobusiness']:,} تومان\n"
                if prices['kasrapars']:
                    message += f"• کسرا پارس: {prices['kasrapars']:,} تومان\n"

            # ایجاد کیبورد برای بازگشت
            keyboard = [[InlineKeyboardButton("🔙 بازگشت به لیست", callback_data="back_to_list")], [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back_to_menu")]]
            await query.message.edit_text(
                message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

# handler برای پیام‌های عادی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    message_text = update.message.text
    authorized_users = load_authorized_users()

    if message_text == "🔍 جستجوی محصول":
        await handle_search(update, context)
        return

    if context.user_data.get('state') == SEARCHING:
        # جستجو بر اساس متن وارد شده
        search_query = message_text.strip()
        products = await get_products_list(search_query)
        if not products:
            await update.message.reply_text(
                "❌ هیچ محصولی با این عبارت یافت نشد.",
                reply_markup=get_keyboard()
            )
            context.user_data['state'] = None
            return
        await update.message.reply_text(
            "📱 لطفاً محصول مورد نظر خود را انتخاب کنید:",
            reply_markup=get_products_keyboard(products)
        )
        context.user_data['products'] = products
        context.user_data['state'] = SELECTING_PRODUCT
        return

    if message_text == "🔄 شروع بروزرسانی":
        # بررسی دسترسی کاربر
        if user_id not in authorized_users:
            await update.message.reply_text(
                "❌ <b>شما مجاز به استفاده از این قابلیت نیستید!</b>",
                parse_mode='HTML'
            )
            return

        # --- محدودیت بروزرسانی ---
        lock_data = load_update_lock()
        now = int(time.time())
        if lock_data.get("locked", False):
            await update.message.reply_text(
                "⏳ <b>در حال حاضر یک بروزرسانی دیگر در حال انجام است. لطفاً کمی بعد دوباره تلاش کنید.</b>",
                parse_mode='HTML'
            )
            return
        if now - lock_data.get("last_update", 0) < UPDATE_COOLDOWN_SECONDS:
            minutes_left = int((UPDATE_COOLDOWN_SECONDS - (now - lock_data.get("last_update", 0))) / 60)
            await update.message.reply_text(
                f"⏰ <b>بروزرسانی فقط هر ۱ ساعت یکبار مجاز است. لطفاً {minutes_left} دقیقه دیگر دوباره تلاش کنید.</b>",
                parse_mode='HTML'
            )
            return
        # فعال کردن قفل
        lock_data["locked"] = True
        save_update_lock(lock_data)

        await update.message.reply_text("🔄 <b>در حال بروزرسانی...</b>", parse_mode='HTML')
        try:
            # اجرای اسکریپت بروزرسانی
            result = subprocess.run(["python", "scrap.py"], capture_output=True, text=True)
            if result.returncode == 0:
                await update.message.reply_text(
                    "✅ <b>بروزرسانی با موفقیت انجام شد!</b>",
                    parse_mode='HTML'
                )
                # ثبت زمان آخرین بروزرسانی و آزاد کردن قفل
                lock_data["locked"] = False
                lock_data["last_update"] = int(time.time())
                save_update_lock(lock_data)
                # ارسال خودکار فایل اکسل بعد از بروزرسانی موفق
                try:
                    if os.path.exists(EXCEL_FILE_PATH):
                        await update.message.reply_text("📊 <b>این فایل خدمت شما:</b>", parse_mode='HTML')
                        with open(EXCEL_FILE_PATH, 'rb') as excel_file:
                            await update.message.reply_document(
                                document=excel_file,
                                filename="scrap.xlsx"
                            )
                    else:
                        await update.message.reply_text(
                            "❌ <b>فایل اکسل یافت نشد!</b>",
                            parse_mode='HTML'
                        )
                except Exception as e:
                    await update.message.reply_text(
                        f"❌ <b>خطا در ارسال فایل:</b>\n<code>{str(e)}</code>",
                        parse_mode='HTML'
                    )
            else:
                await update.message.reply_text(
                    f"❌ <b>خطا در بروزرسانی:</b>\n<code>{result.stderr}</code>",
                    parse_mode='HTML'
                )
                # آزاد کردن قفل در صورت خطا
                lock_data["locked"] = False
                save_update_lock(lock_data)
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>خطا در بروزرسانی:</b>\n<code>{str(e)}</code>",
                parse_mode='HTML'
            )
            # آزاد کردن قفل در صورت خطا
            lock_data["locked"] = False
            save_update_lock(lock_data)
            
    elif message_text == "⏰ آخرین بروزرسانی":
        try:
            if os.path.exists(EXCEL_FILE_PATH):
                # دریافت زمان آخرین تغییر فایل
                file_time = datetime.fromtimestamp(os.path.getmtime(EXCEL_FILE_PATH))
                time_diff = datetime.now() - file_time
                hours = time_diff.total_seconds() / 3600
                
                if hours < 1:
                    minutes = int(time_diff.total_seconds() / 60)
                    message = f"⏰ <b>آخرین بروزرسانی</b> {minutes} دقیقه پیش انجام شده است."
                else:
                    message = f"⏰ <b>آخرین بروزرسانی</b> {int(hours)} ساعت پیش انجام شده است."
            else:
                message = "⏰ <b>هنوز بروزرسانی انجام نشده است.</b>"
        except Exception as e:
            message = f"❌ <b>خطا در بررسی زمان بروزرسانی:</b>\n<code>{str(e)}</code>"
        await update.message.reply_text(message, parse_mode='HTML')
        
    elif message_text == "📊 دریافت فایل اکسل":
        await update.message.reply_text("📊 <b>در حال ارسال فایل اکسل...</b>", parse_mode='HTML')
        try:
            if os.path.exists(EXCEL_FILE_PATH):
                with open(EXCEL_FILE_PATH, 'rb') as excel_file:
                    await update.message.reply_document(
                        document=excel_file,
                        filename="scrap.xlsx"
                    )
            else:
                await update.message.reply_text(
                    "❌ <b>فایل اکسل یافت نشد!</b>",
                    parse_mode='HTML'
                )
        except Exception as e:
            await update.message.reply_text(
                f"❌ <b>خطا در ارسال فایل:</b>\n<code>{str(e)}</code>",
                parse_mode='HTML'
            )
        
    elif message_text == "ℹ️ درباره ربات":
        about_text = """
🤖 <b>درباره ربات جستجوی قیمت موبایل</b>

این ربات به شما کمک می‌کند آخرین قیمت و موجودی انواع گوشی موبایل را از چندین فروشگاه معتبر به راحتی جستجو و مقایسه کنید.

<b>امکانات ربات:</b>
• 🔍 جستجوی هوشمند محصول با تایپ بخشی از مدل یا نام گوشی
• 📱 نمایش مدل، ظرفیت (حجم)، رنگ‌بندی و قیمت هر رنگ در فروشگاه‌های مختلف
• 🏷️ مشاهده قیمت‌های فروشگاه‌های: همراه‌تل، فرنا، آسود، تکنوبیزنس، کسرا پارس
• 📊 دریافت فایل اکسل کامل آخرین قیمت‌ها
• ⏰ مشاهده زمان آخرین بروزرسانی قیمت‌ها
• 🔄 بروزرسانی قیمت‌ها (ویژه کاربران مجاز)
• 🛡️ مدیریت کاربران مجاز توسط ادمین
• 🏠 بازگشت سریع به منوی اصلی در هر مرحله

<b>دستورات:</b>
• /start - شروع ربات و ثبت شما
• /myid - نمایش شناسه عددی شما
• /admin - دستورات مدیریتی (فقط برای ادمین)

<b>نکته:</b>
برای جستجوی محصول کافیست روی "جستجوی محصول" بزنید و بخشی از مدل یا نام گوشی را تایپ کنید تا لیست محصولات مرتبط را به صورت دکمه دریافت کنید.

<b>توسعه‌دهنده:</b>
@aminfree
"""
        await update.message.reply_text(about_text, parse_mode='HTML')
    else:
        # ارسال پیام نامعتبر به ادمین
        await notify_admin_about_invalid_message(context, update.message.from_user, message_text)
        await update.message.reply_text("❌ <b>گزینه نامعتبر!</b>", parse_mode='HTML')

# ارسال اطلاعات کاربر جدید به ادمین
async def notify_admin_about_new_user(context: ContextTypes.DEFAULT_TYPE, user):
    user_id = str(user.id)
    username = user.username or "بدون نام کاربری"
    first_name = user.first_name or "بدون نام"
    last_name = user.last_name or ""
    
    message = f"""
👤 <b>کاربر جدید وارد ربات شد!</b>

🆔 شناسه عددی: <code>{user_id}</code>
👤 نام: {first_name}
👥 نام خانوادگی: {last_name}
🔖 نام کاربری: @{username}

برای اضافه کردن دسترسی بروزرسانی، از دستور زیر استفاده کنید:
<code>/admin add {user_id}</code>
"""
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message, parse_mode='HTML')

# ارسال پیام نامعتبر به ادمین
async def notify_admin_about_invalid_message(context: ContextTypes.DEFAULT_TYPE, user, message_text):
    user_id = str(user.id)
    username = user.username or "بدون نام کاربری"
    first_name = user.first_name or "بدون نام"
    last_name = user.last_name or ""
    
    admin_message = f"""
⚠️ <b>پیام نامعتبر از کاربر:</b>

👤 <b>اطلاعات کاربر:</b>
🆔 شناسه عددی: <code>{user_id}</code>
👤 نام: {first_name}
👥 نام خانوادگی: {last_name}
🔖 نام کاربری: @{username}

📝 <b>پیام ارسالی:</b>
<code>{message_text}</code>
"""
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message, parse_mode='HTML')

# دستور /myid برای نمایش شناسه کاربر
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "بدون نام کاربری"
    first_name = update.message.from_user.first_name or "بدون نام"
    
    message = f"""
👤 <b>اطلاعات کاربری شما:</b>

🆔 شناسه عددی: <code>{user_id}</code>
👤 نام: {first_name}
🔖 نام کاربری: @{username}

برای اضافه کردن دسترسی بروزرسانی، این شناسه را به ادمین ارسال کنید.
"""
    await update.message.reply_text(message, parse_mode='HTML')

# دستورات ادمین
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ <b>شما دسترسی ادمین ندارید!</b>", parse_mode='HTML')
        return

    if not context.args:
        message = """
👑 <b>دستورات ادمین:</b>

/add [شناسه کاربر] - اضافه کردن کاربر به لیست مجاز
/remove [شناسه کاربر] - حذف کاربر از لیست مجاز
/list - نمایش لیست کاربران مجاز
/users - نمایش لیست تمام کاربران
"""
        await update.message.reply_text(message, parse_mode='HTML')
        return

    command = context.args[0].lower()
    authorized_users = load_authorized_users()
    users = load_users()

    if command == "add" and len(context.args) > 1:
        new_user = context.args[1]
        if new_user not in authorized_users:
            authorized_users.append(new_user)
            save_authorized_users(authorized_users)
            await update.message.reply_text(f"✅ <b>کاربر {new_user} به لیست مجاز اضافه شد.</b>", parse_mode='HTML')
        else:
            await update.message.reply_text("⚠️ <b>این کاربر قبلاً در لیست مجاز است.</b>", parse_mode='HTML')

    elif command == "remove" and len(context.args) > 1:
        user_to_remove = context.args[1]
        if user_to_remove in authorized_users and user_to_remove != ADMIN_CHAT_ID:
            authorized_users.remove(user_to_remove)
            save_authorized_users(authorized_users)
            await update.message.reply_text(f"✅ <b>کاربر {user_to_remove} از لیست مجاز حذف شد.</b>", parse_mode='HTML')
        elif user_to_remove == ADMIN_CHAT_ID:
            await update.message.reply_text("❌ <b>نمی‌توان ادمین را از لیست مجاز حذف کرد!</b>", parse_mode='HTML')
        else:
            await update.message.reply_text("⚠️ <b>این کاربر در لیست مجاز نیست.</b>", parse_mode='HTML')

    elif command == "list":
        users_list = "\n".join([f"• {user}" for user in authorized_users])
        message = f"""
👥 <b>لیست کاربران مجاز:</b>

{users_list}
"""
        await update.message.reply_text(message, parse_mode='HTML')

    elif command == "users":
        if not users:
            await update.message.reply_text("📝 <b>هنوز هیچ کاربری در ربات ثبت نشده است.</b>", parse_mode='HTML')
            return

        users_list = []
        for user_id, user_data in users.items():
            username = user_data.get('username', 'بدون نام کاربری')
            first_name = user_data.get('first_name', 'بدون نام')
            last_name = user_data.get('last_name', '')
            is_authorized = "✅" if user_id in authorized_users else "❌"
            users_list.append(f"• {is_authorized} {user_id} - {first_name} {last_name} (@{username})")

        message = f"""
👥 <b>لیست تمام کاربران:</b>

{chr(10).join(users_list)}

✅ = کاربر مجاز
❌ = کاربر غیرمجاز
"""
        await update.message.reply_text(message, parse_mode='HTML')

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)
    
    # ذخیره اطلاعات کاربر
    users = load_users()
    users[user_id] = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'joined_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_users(users)
    
    # ارسال اطلاعات به ادمین
    await notify_admin_about_new_user(context, user)
    
    welcome_message = """
👋 به ربات خوش آمدید!

🔍 برای جستجوی محصولات، روی دکمه "جستجوی محصول" کلیک کنید.
🔄 برای بروزرسانی قیمت‌ها، روی دکمه "شروع بروزرسانی" کلیک کنید.
⏰ برای مشاهده آخرین بروزرسانی، روی دکمه "آخرین بروزرسانی" کلیک کنید.
📊 برای دریافت فایل اکسل، روی دکمه "دریافت فایل اکسل" کلیک کنید.
"""
    await update.message.reply_text(welcome_message, reply_markup=get_keyboard())

# اجرای ربات
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_product_selection))

    print("The robot was successfully launched.🚀")
    app.run_polling()
