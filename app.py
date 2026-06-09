import sqlite3
from collections import Counter
from datetime import datetime
from os import environ
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = environ.get("DATABASE_URL")
SQLITE_DATABASE = Path(
    environ.get("STARBUCKS_DATABASE", BASE_DIR / "data" / "drink_orders.sqlite3")
)

DRINK_OPTIONS = [
    "美式咖啡",
    "那堤",
    "焦糖瑪奇朵",
    "摩卡",
    "卡布奇諾",
    "冷萃咖啡",
    "抹茶那堤",
    "伯爵茶那堤",
    "經典紅茶那堤",
    "可可瑪奇朵",
    "星冰樂",
]

TEMPERATURE_OPTIONS = ["冷", "熱"]
SIZE_OPTIONS = ["中杯", "大杯", "特大杯"]
SUGAR_OPTIONS = ["正常糖", "少糖", "半糖", "微糖", "無糖"]
ICE_OPTIONS = ["正常冰", "少冰", "微冰", "去冰"]
ORDER_CLOSED_KEY = "order_closed"


app = Flask(__name__)
app.config["SECRET_KEY"] = environ.get("SECRET_KEY", "change-me-for-production")


def is_postgres():
    return bool(DATABASE_URL)


def sql(query):
    return query.replace("?", "%s") if is_postgres() else query


def get_db():
    if "db" not in g:
        if is_postgres():
            from psycopg import connect
            from psycopg.rows import dict_row

            postgres_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
            g.db = connect(postgres_url, row_factory=dict_row)
        else:
            SQLITE_DATABASE.parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(str(SQLITE_DATABASE))
            g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    if is_postgres():
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                drink TEXT NOT NULL,
                temperature TEXT NOT NULL,
                size TEXT NOT NULL,
                sugar TEXT NOT NULL,
                ice TEXT NOT NULL,
                note TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )
    else:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                drink TEXT NOT NULL,
                temperature TEXT NOT NULL,
                size TEXT NOT NULL,
                sugar TEXT NOT NULL,
                ice TEXT NOT NULL,
                note TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            )
            """
        )

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    db.execute(
        sql("INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO NOTHING"),
        (ORDER_CLOSED_KEY, "0"),
    )
    db.commit()


@app.before_request
def ensure_database():
    init_db()


def clean_required(value):
    return (value or "").strip()


def get_setting(key, default=""):
    row = get_db().execute(
        sql("SELECT value FROM app_settings WHERE key = ?"),
        (key,),
    ).fetchone()
    return row["value"] if row else default


def set_setting(key, value):
    get_db().execute(
        sql(
            """
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """
        ),
        (key, value),
    )


def is_order_closed():
    return get_setting(ORDER_CLOSED_KEY, "0") == "1"


def set_order_closed(closed):
    set_setting(ORDER_CLOSED_KEY, "1" if closed else "0")


def build_copy_text(orders):
    if not orders:
        return "目前尚無飲料統計。"

    lines = ["星巴克飲料統計"]
    lines.append("")
    lines.append("品項統計：")
    for drink, count in Counter(order["drink"] for order in orders).most_common():
        lines.append(f"{drink} x {count}")

    lines.append("")
    lines.append("明細：")
    for order in orders:
        note = f"｜備註：{order['note']}" if order["note"] else ""
        lines.append(
            f"{order['name']}：{order['drink']}｜{order['temperature']}｜"
            f"{order['size']}｜{order['sugar']}｜{order['ice']}{note}"
        )
    return "\n".join(lines)


def render_order_form(form=None):
    return render_template(
        "index.html",
        drink_options=DRINK_OPTIONS,
        temperature_options=TEMPERATURE_OPTIONS,
        size_options=SIZE_OPTIONS,
        sugar_options=SUGAR_OPTIONS,
        ice_options=ICE_OPTIONS,
        form=form or {},
        order_closed=is_order_closed(),
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if is_order_closed():
        return render_order_form(request.form if request.method == "POST" else {})

    if request.method == "POST":
        name = clean_required(request.form.get("name"))
        selected_drink = clean_required(request.form.get("drink"))
        other_drink = clean_required(request.form.get("other_drink"))
        drink = other_drink if selected_drink == "其他" else selected_drink
        temperature = clean_required(request.form.get("temperature"))
        size = clean_required(request.form.get("size"))
        sugar = clean_required(request.form.get("sugar"))
        ice = clean_required(request.form.get("ice"))
        note = clean_required(request.form.get("note"))

        if not all([name, drink, temperature, size, sugar, ice]):
            flash("請填寫姓名、飲料品項與所有選項。")
            return render_order_form(request.form)

        get_db().execute(
            sql(
                """
                INSERT INTO orders
                    (name, drink, temperature, size, sugar, ice, note, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    drink = excluded.drink,
                    temperature = excluded.temperature,
                    size = excluded.size,
                    sugar = excluded.sugar,
                    ice = excluded.ice,
                    note = excluded.note,
                    updated_at = excluded.updated_at
                """
            ),
            (
                name,
                drink,
                temperature,
                size,
                sugar,
                ice,
                note,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        get_db().commit()
        return render_template("thanks.html", name=name)

    return render_order_form()


@app.route("/admin")
def admin():
    orders = get_db().execute(
        "SELECT * FROM orders ORDER BY updated_at DESC, name ASC"
    ).fetchall()
    drink_counts = Counter(order["drink"] for order in orders)
    return render_template(
        "admin.html",
        orders=orders,
        drink_counts=drink_counts.most_common(),
        copy_text=build_copy_text(orders),
        order_closed=is_order_closed(),
    )


@app.post("/admin/toggle-closed")
def toggle_order_closed():
    closed = request.form.get("closed") == "1"
    set_order_closed(closed)
    get_db().commit()
    flash("已停止填寫。" if closed else "已恢復可填寫。")
    return redirect(url_for("admin"))


@app.post("/admin/clear")
def clear_orders():
    db = get_db()
    db.execute("DELETE FROM orders")
    set_order_closed(False)
    db.commit()
    flash("已清空本次統計，並恢復可填寫狀態。")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
