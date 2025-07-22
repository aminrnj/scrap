from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, get_flashed_messages
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import subprocess, json
from datetime import datetime
import pytz
import jdatetime
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ایجاد اپلیکیشن و تنظیمات آن
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-super-secret-key-1234'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///datasitenews5.db"

# ایجاد اتصال به دیتابیس
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=False)
db = SQLAlchemy(app)

# افزودن Flask-Migrate برای مدیریت migration
from flask_migrate import Migrate
migrate = Migrate(app, db)

# تنظیمات ورود کاربران
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# تابع دریافت زمان تهران
def tehran_now():
    return datetime.now(pytz.timezone('Asia/Tehran'))

# مدل کاربر به‌روز شده با دو فیلد جدید
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(256))
    can_update = db.Column(db.Boolean, default=False)
    can_download_excel = db.Column(db.Boolean, default=False)
    can_request_scrap = db.Column(db.Boolean, default=False)
    can_view_predefined_percent = db.Column(db.Boolean, default=True)
    can_use_custom_percent = db.Column(db.Boolean, default=True)

# مدل درخواست‌های اسکرپ
class ScrapRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_name = db.Column(db.String(200))
    links = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=tehran_now)

    user = db.relationship('User', backref='scrap_requests')

# مدل تیکت‌ها
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    admin_response = db.Column(db.Text)  # پاسخ مدیر
    status = db.Column(db.String(50), default="در انتظار پاسخ")
    date_created = db.Column(db.DateTime, default=tehran_now)

    user = db.relationship('User', backref='tickets')
@app.route("/api/weekly-stats")
@login_required
def weekly_stats():
    import datetime
    week_start = datetime.datetime.now(pytz.timezone('Asia/Tehran')) - datetime.timedelta(days=7)
    week_start_str = week_start.strftime('%Y-%m-%d %H:%M:%S')

    def safe_int(val):
        try:
            return int(str(val).replace(",", "").strip())
        except Exception:
            return 0

    query = text("""
    WITH weekly AS (
      SELECT * FROM products WHERE date >= :week_start
    )
    SELECT 
      model,
      (SELECT min_price FROM weekly w2 WHERE w2.model = weekly.model ORDER BY date ASC LIMIT 1) as start_price,
      (SELECT min_price FROM weekly w2 WHERE w2.model = weekly.model ORDER BY date DESC LIMIT 1) as latest_price,
      (SELECT MAX(min_price) FROM weekly w2 WHERE w2.model = weekly.model) as max_price,
      (SELECT MIN(min_price) FROM weekly w2 WHERE w2.model = weekly.model) as min_recorded_price,
      (SELECT date FROM weekly w2 WHERE w2.model = weekly.model ORDER BY date DESC LIMIT 1) as latest_date,
      (SELECT 
          ((CASE WHEN hamrahtel_price > 0 THEN 1 ELSE 0 END) +
           (CASE WHEN farnaa_price > 0 THEN 1 ELSE 0 END) +
           (CASE WHEN aasood_price > 0 THEN 1 ELSE 0 END) +
           (CASE WHEN technobusiness_price > 0 THEN 1 ELSE 0 END) +
           (CASE WHEN kasrapars_price > 0 THEN 1 ELSE 0 END))
        FROM weekly w2 
        WHERE w2.model = weekly.model 
        ORDER BY date DESC LIMIT 1) as availability
    FROM weekly
    GROUP BY model;
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"week_start": week_start_str}).mappings().all()
        stats_data = []
        for row in result:
            model = row.get('model', None) or (row[0] if row else None)
            start_price = safe_int(row.get('start_price') or 0)
            latest_price = safe_int(row.get('latest_price') or 0)
            max_price = safe_int(row.get('max_price') or 0)
            min_recorded_price = safe_int(row.get('min_recorded_price') or 0)
            delta = latest_price - start_price
            volatility = max_price - min_recorded_price
            availability = safe_int(row.get('availability') or 0)
            latest_date = row.get('latest_date')
            stats_data.append({
                "model": model,
                "start_price": start_price,
                "latest_price": latest_price,
                "delta": delta,
                "volatility": volatility,
                "availability": availability,
                "latest_date": latest_date
            })
  
    # دسته‌بندی‌های مختلف:
    increase = sorted([x for x in stats_data if x["delta"] > 0], key=lambda x: x["delta"], reverse=True)[:5]
    decrease = sorted([x for x in stats_data if x["delta"] < 0], key=lambda x: x["delta"])[:5]
    volatility_list = sorted(stats_data, key=lambda x: x["volatility"], reverse=True)[:5]
    max_avail = sorted(stats_data, key=lambda x: x["availability"], reverse=True)[:5]
    min_avail = sorted(stats_data, key=lambda x: x["availability"])[:5]
    newest = sorted(stats_data, key=lambda x: x["latest_date"], reverse=True)[:5]
    return jsonify({
        "increase": increase,
        "decrease": decrease,
        "volatility": volatility_list,
        "max_availability": max_avail,
        "min_availability": min_avail,
        "newest": newest
    })



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            send_telegram_message(f"✅ ورود موفق توسط: <b>{username}</b>\n📍 IP: {request.remote_addr}")
            return render_template('login.html', success=True)
        else:
            send_telegram_message(f"❌ تلاش ناموفق برای ورود با نام: <b>{username}</b>\n📍 IP: {request.remote_addr}")
            return render_template('login.html', error="نام کاربری یا رمز عبور اشتباه است!")

    return render_template("login.html")

@app.route("/login-success")
@login_required
def login_success():
    return render_template("login.html", success=True)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def index():
    # ارسال فیلدهای جدید به قالب
    return render_template("index.html", 
                           username=current_user.username,
                           can_update=current_user.can_update,
                           can_download_excel=current_user.can_download_excel,
                           can_request_scrap=current_user.can_request_scrap,
                           can_view_predefined_percent=current_user.can_view_predefined_percent,
                           can_use_custom_percent=current_user.can_use_custom_percent)

@app.route("/api/products")
@login_required
def get_products():
    search_query = request.args.get("search", "").lower()
    query = text("""
        SELECT * FROM products
        WHERE date = (SELECT MAX(date) FROM products)
        AND (:search = '' OR LOWER(model) LIKE :search OR LOWER(category) LIKE :search)
        ORDER BY date DESC
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"search": f"%{search_query}%"}).fetchall()
        column_names = [col[1] for col in connection.execute(text("PRAGMA table_info(products)")).fetchall()]
        products = [dict(zip(column_names, row)) for row in result]
    return jsonify(products)

@app.route("/update", methods=["POST"])
@login_required
def update_data():
    try:
        result = subprocess.run(["python", "scrap.py"], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "بروزرسانی با موفقیت انجام شد!"})
        else:
            return jsonify({"status": "error", "message": result.stderr})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/product-history/<path:model>")
@login_required
def product_history(model):
    query = text("""
        SELECT date, hamrahtel_price, farnaa_price, aasood_price, technobusiness_price, kasrapars_price, min_price
        FROM products WHERE model = :model ORDER BY date
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"model": model}).fetchall()
        columns = ["date", "hamrahtel_price", "farnaa_price", "aasood_price", "technobusiness_price", "kasrapars_price", "min_price"]
        history = [dict(zip(columns, row)) for row in result]
    return jsonify(history)

@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if current_user.username != "amin":
        return "شما اجازه دسترسی ندارید!", 403

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="نام کاربری قبلاً وجود دارد.")

        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return render_template('register.html', success="کاربر جدید ساخته شد!")

    return render_template("register.html")

@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if current_user.username != "amin":
        return "شما اجازه دسترسی ندارید!", 403

    if request.method == "POST":
        user = User.query.get(request.form.get('user_id'))
        user.can_update = 'can_update' in request.form
        user.can_download_excel = 'can_download_excel' in request.form
        user.can_request_scrap = 'can_request_scrap' in request.form
        user.can_view_predefined_percent = 'can_view_predefined_percent' in request.form
        user.can_use_custom_percent = 'can_use_custom_percent' in request.form
        db.session.commit()

    users_list = User.query.all()
    return render_template("users.html", users=users_list)

@app.route("/change-password/<int:user_id>", methods=["POST"])
@login_required
def change_password(user_id):
    if current_user.username != "amin":
        return "شما اجازه دسترسی ندارید!", 403

    user = User.query.get_or_404(user_id)
    user.password = generate_password_hash(request.form['password'])
    db.session.commit()

    return redirect(url_for('users'))

@app.route("/scrap-request", methods=["GET", "POST"])
@login_required
def scrap_request():
    if not current_user.can_request_scrap:
        return "شما اجازه دسترسی به این صفحه را ندارید!", 403

    if request.method == "POST":
        product_name = request.form.get('product_name')
        links = request.form.getlist('links[]')

        new_request = ScrapRequest(
            user_id=current_user.id,
            product_name=product_name,
            links=json.dumps(links)
        )
        db.session.add(new_request)
        db.session.commit()

        send_telegram_message(
            f"📥 درخواست جدید اسکرپ ثبت شد!\n"
            f"👤 کاربر: {current_user.username}\n"
            f"📦 محصول: {product_name}\n"
            f"🔗 لینک‌ها:\n" + '\n'.join(links)
        )

        return render_template("scrap_request.html", success="درخواست با موفقیت ارسال شد.")

    return render_template("scrap_request.html")

@app.route("/view-requests")
@login_required
def view_requests():
    if current_user.username != "amin":
        return "شما اجازه دسترسی به این صفحه را ندارید!", 403

    requests = ScrapRequest.query.order_by(ScrapRequest.date_created.desc()).all()
    return render_template("view_requests.html", requests=requests, json=json)

@app.template_filter('to_jalali')
def to_jalali(dt):
    if dt is None:
        return ""
    jdate = jdatetime.datetime.fromgregorian(datetime=dt)
    return jdate.strftime('%Y/%m/%d - %H:%M')

last_dollar_price = None

def persian_to_english_digits(s: str) -> str:
    fa = "۰۱۲۳۴۵۶۷۸۹"
    en = "0123456789"
    return s.translate(str.maketrans(fa, en))

@app.route('/api/dollar-price')
def get_dollar_price():
    global last_dollar_price
    url = 'https://www.tgju.org/%D9%82%DB%8C%D9%85%D8%AA-%D8%AF%D9%84%D8%A7%D8%B1'
    try:
        # تنظیمات Selenium برای ران کردن کروم در حالت headless
        chrome_opts = Options()
        chrome_opts.add_argument('--headless')
        chrome_opts.add_argument('--no-sandbox')
        chrome_opts.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_opts)

        # بازکردن صفحه و انتظار حداکثر 4 ثانیه برای بارگذاری تگ قیمت
        driver.get(url)
        WebDriverWait(driver, 4).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'tr[data-market-nameslug="price_dollar_rl"] td.nf')
            )
        )
        price_text = driver.find_element(
            By.CSS_SELECTOR, 
            'tr[data-market-nameslug="price_dollar_rl"] td.nf'
        ).text
        driver.quit()

        # تبدیل ارقام فارسی و استخراج فقط اعداد
        price_text = persian_to_english_digits(price_text.strip())
        digits = re.sub(r"[^\d]", "", price_text)
        if not digits:
            return jsonify({"error": "قیمت استخراج نشد"}), 500

        # تقسیم ریال به تومان
        current_price = int(digits) // 10

        # تعیین جهت نوسان
        price_change = None
        if last_dollar_price is not None:
            if current_price > last_dollar_price:
                price_change = "up"
            elif current_price < last_dollar_price:
                price_change = "down"

        last_dollar_price = current_price

        # فرمت فارسی عدد
        formatted_price = f"{current_price:,}".replace(",", "،")
        send_telegram_message(f"قیمت دلار : {formatted_price} تومان", chat_id=CHANNEL_CHAT_ID)

        return jsonify({
            "price": current_price,
            "price_change": price_change
        })

    except Exception as e:
        # اگر Selenium باز ماند، حتما ببندید
        try:
            driver.quit()
        except:
            pass
        return jsonify({"error": str(e)}), 500




@app.route("/ticket", methods=["GET", "POST"])
@login_required
def ticket():
    if request.method == "POST":
        subject = request.form.get('subject')
        description = request.form.get('description')
        if not subject or not description:
            return render_template("ticket.html", error="لطفاً موضوع و توضیحات را وارد کنید.", tickets=Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.date_created.desc()).all())
        
        new_ticket = Ticket(
            user_id=current_user.id,
            subject=subject,
            description=description
        )
        db.session.add(new_ticket)
        db.session.commit()

        send_telegram_message(
            f"📩 تیکت جدید ثبت شد!\n"
            f"👤 کاربر: {current_user.username}\n"
            f"📝 موضوع: {subject}\n"
            f"💬 توضیحات:\n{description}"
        )
        return render_template("ticket.html", success="تیکت شما با موفقیت ارسال شد.", tickets=Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.date_created.desc()).all())
    
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.date_created.desc()).all()
    return render_template("ticket.html", tickets=tickets)

@app.route('/view-tickets')
@login_required
def view_tickets():
    if current_user.username != "amin":
        return "شما اجازه دسترسی ندارید!", 403
    tickets = Ticket.query.order_by(Ticket.date_created.desc()).all()
    return render_template("view_tickets.html", tickets=tickets)

@app.route('/delete-ticket/<int:ticket_id>')
@login_required
def delete_ticket(ticket_id):
    if current_user.username != "amin":
        return "شما اجازه دسترسی به این صفحه را ندارید!", 403
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return redirect(url_for('view_tickets'))

@app.route("/api/categories")
@login_required
def get_categories():
    query = text("SELECT DISTINCT category FROM products")
    with engine.connect() as connection:
        result = connection.execute(query).fetchall()
        categories = [row[0] for row in result if row[0]]
    return jsonify(categories)

@app.route('/manage-tickets', methods=['GET', 'POST'])
@login_required
def manage_tickets():
    if current_user.username != "amin":
        return "شما اجازه دسترسی به این صفحه را ندارید!", 403

    if request.method == "POST":
        ticket_id = request.form.get('ticket_id')
        new_status = request.form.get('status')
        admin_response = request.form.get('admin_response')
        ticket = Ticket.query.get_or_404(ticket_id)
        ticket.status = new_status
        ticket.admin_response = admin_response
        db.session.commit()
        return redirect(url_for('manage_tickets'))

    tickets = Ticket.query.order_by(Ticket.date_created.desc()).all()
    return render_template("manage_tickets.html", tickets=tickets)

TELEGRAM_BOT_TOKEN = '7634348306:AAHTG2-HAtKt9hl_q8yFZlgncdM4DcA_iA4'
ADMIN_CHAT_ID = '2821814'  # آیدی تلگرام یا گروه
CHANNEL_CHAT_ID = '@Dollardata'  # شناسه کانال

def send_telegram_message(text, chat_id=ADMIN_CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ خطا در ارسال پیام تلگرام:", e)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="amin").first():
            admin = User(username="amin", password=generate_password_hash("Amin220088"),
                         can_update=True, can_download_excel=True, can_request_scrap=True,
                         can_view_predefined_percent=True, can_use_custom_percent=True)
            db.session.add(admin)
            db.session.commit()

    app.run(host="192.168.100.16", port=8080)
