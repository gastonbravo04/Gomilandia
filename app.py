import os
import sys
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)
app.secret_key = "gomilandia_secret_key_2026_mendoza"

# Carpeta para guardar imágenes que sube el usuario en el admin
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DB_PATH = os.path.join(app.root_path, "gomilandia.db")

# Credenciales de Administrador
ADMIN_USER = "gomilandia"
ADMIN_PASS = "gomitas2026"
WHATSAPP_NUMBER = "542604594824"


# Configuración CORS para permitir peticiones si el frontend se aloja en Netlify
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa la base de datos y migra columnas nuevas automáticamente."""
    conn = get_db()
    cursor = conn.cursor()

    # Tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tag TEXT NOT NULL,
            emoji TEXT NOT NULL,
            price INTEGER NOT NULL,
            desc TEXT,
            img TEXT,
            in_stock INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Tabla de pedidos / ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_phone TEXT NOT NULL,
            card_occasion TEXT,
            card_message TEXT,
            payment_method TEXT NOT NULL,
            notes TEXT,
            items_json TEXT NOT NULL,
            total_price INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendiente'
        )
    """)

    # Migración segura: verificar si existen columnas nuevas en caso de BD existente
    cursor.execute("PRAGMA table_info(products)")
    prod_columns = [col["name"] for col in cursor.fetchall()]
    if "in_stock" not in prod_columns:
        cursor.execute("ALTER TABLE products ADD COLUMN in_stock INTEGER NOT NULL DEFAULT 1")

    cursor.execute("PRAGMA table_info(orders)")
    order_columns = [col["name"] for col in cursor.fetchall()]
    if "status" not in order_columns:
        cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pendiente'")

    # Cargar productos iniciales si está vacía
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    if count == 0:
        default_products = [
            ("Mini Sweet Cup", "Vaso", "🥤", 5000, "Vasito individual colmado de gomitas variadas. ¡Ideal para llevar y compartir!", "/static/img/mini_cup.jpg", 1),
            ("Sweet Cup", "Vaso", "🥤", 6000, "Vaso grande con cúpula, cargado de las mejores gomitas y gusanos ácidos coloridos.", "/static/img/sweet_cup.jpg", 1),
            ("Sweet Shot", "Mini", "🍬", 3500, "Frasquito tierno perfecto para un antojo dulce o un pequeño detalle sorpresa.", "/static/img/sweet_shot.jpg", 1),
            ("Corazón Gomilandia", "Especial", "💖", 5000, "Caja corazón transparente con cinta rosa y gomitas frutales. Regalo inolvidable.", "/static/img/corazon.jpg", 1),
            ("Ensalada Gomilandia", "Ensalada", "🌈", 11000, "Contenedor cuadrado con mezcla súper abundante de ositos, aros, cintas y estrellas.", "/static/img/ensalada.jpg", 1),
            ("Picada Gomi Mix", "Picada", "🎡", 12500, "Bandeja compartimentada con 5+ variedades gourmet. La reina de tus juntadas.", "/static/img/picada.jpg", 1)
        ]
        cursor.executemany("""
            INSERT INTO products (name, tag, emoji, price, desc, img, in_stock)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_products)

    conn.commit()
    conn.close()


# Inicializar la base de datos de manera automática
init_db()


# ══════════════════════════════════════════════════
# RUTAS DE PÁGINA (FRONTEND PÚBLICO)
# ══════════════════════════════════════════════════

@app.route("/")
def index():
    """Página principal de Gomilandia con el catálogo actualizado."""
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
    conn.close()
    return render_template("index.html", products=products, wa_number=WHATSAPP_NUMBER)


# ══════════════════════════════════════════════════
# APARTADO DEDICADO DEL ADMINISTRADOR (/admin)
# ══════════════════════════════════════════════════

@app.route("/admin")
def admin_panel():
    """Apartado exclusivo para el administrador de Gomilandia."""
    if not session.get("is_admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
    orders_rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()

    orders = []
    total_revenue = 0
    pending_orders = 0
    for r in orders_rows:
        d = dict(r)
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        d["order_items"] = d["items"]
        orders.append(d)
        total_revenue += d.get("total_price", 0)
        if d.get("status", "pendiente") == "pendiente":
            pending_orders += 1

    out_of_stock_count = sum(1 for p in products if p["in_stock"] == 0)

    stats = {
        "total_revenue": total_revenue,
        "total_orders": len(orders),
        "pending_orders": pending_orders,
        "total_products": len(products),
        "out_of_stock_count": out_of_stock_count
    }

    return render_template("admin.html", products=products, orders=orders, stats=stats)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Pantalla de inicio de sesión para el administrador."""
    if request.method == "POST":
        user = request.form.get("user", "").strip()
        pwd = request.form.get("password", "").strip()

        if user == ADMIN_USER and pwd == ADMIN_PASS:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        return render_template("admin_login.html", error="Usuario o contraseña incorrectos")

    if session.get("is_admin"):
        return redirect(url_for("admin_panel"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Cierra la sesión del administrador."""
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


# ══════════════════════════════════════════════════
# APIS PARA PRODUCTOS Y GESTIÓN DE STOCK
# ══════════════════════════════════════════════════

@app.route("/api/products", methods=["GET"])
def get_products():
    """Retorna la lista de productos en formato JSON."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM products ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/products/<int:prod_id>/toggle_stock", methods=["POST"])
def toggle_stock(prod_id):
    """Permite al admin alternar en 1 clic si un producto tiene stock o no."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    conn = get_db()
    cur = conn.cursor()
    prod = cur.execute("SELECT in_stock FROM products WHERE id = ?", (prod_id,)).fetchone()
    if not prod:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    current_stock = prod["in_stock"]
    new_stock = 0 if current_stock == 1 else 1

    cur.execute("UPDATE products SET in_stock = ? WHERE id = ?", (new_stock, prod_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "product_id": prod_id,
        "in_stock": new_stock,
        "message": "Stock actualizado correctamente"
    })


@app.route("/api/products", methods=["POST"])
def create_product():
    """Permite al admin agregar un producto nuevo."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    name = request.form.get("name", "").strip()
    tag = request.form.get("tag", "Gomitas").strip()
    emoji = request.form.get("emoji", "🍬").strip()
    price = int(request.form.get("price", 0))
    desc = request.form.get("desc", "").strip()
    in_stock = 1 if request.form.get("in_stock", "1") in ["1", "true", "on"] else 0

    img_url = "/static/img/logo.jpg"
    if "file" in request.files:
        file = request.files["file"]
        if file and file.filename and allowed_file(file.filename):
            fname = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
            img_url = f"/static/uploads/{fname}"

    if not name or price <= 0:
        return jsonify({"error": "Nombre y precio válidos requeridos"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, tag, emoji, price, desc, img, in_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, tag, emoji, price, desc, img_url, in_stock))
    new_id = cur.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"success": True, "id": new_id, "message": "Producto agregado con éxito"})


@app.route("/api/products/<int:prod_id>", methods=["PUT", "POST"])
def update_product(prod_id):
    """Permite al admin actualizar imágenes, descripciones, precios y stock."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    name = request.form.get("name", "").strip()
    tag = request.form.get("tag", "Gomitas").strip()
    emoji = request.form.get("emoji", "🍬").strip()
    price = int(request.form.get("price", 0))
    desc = request.form.get("desc", "").strip()
    in_stock_raw = request.form.get("in_stock")

    conn = get_db()
    cur = conn.cursor()
    existing = cur.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Producto no encontrado"}), 404

    in_stock = existing["in_stock"]
    if in_stock_raw is not None:
        in_stock = 1 if in_stock_raw in ["1", "true", "on"] else 0

    img_url = existing["img"]
    if "file" in request.files:
        file = request.files["file"]
        if file and file.filename and allowed_file(file.filename):
            fname = f"{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], fname))
            img_url = f"/static/uploads/{fname}"

    cur.execute("""
        UPDATE products
        SET name = ?, tag = ?, emoji = ?, price = ?, desc = ?, img = ?, in_stock = ?
        WHERE id = ?
    """, (name, tag, emoji, price, desc, img_url, in_stock, prod_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Producto actualizado con éxito"})


@app.route("/api/products/<int:prod_id>", methods=["DELETE"])
def delete_product(prod_id):
    """Permite al admin eliminar un producto."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Producto eliminado"})


# ══════════════════════════════════════════════════
# APIS PARA PEDIDOS, MOVIMIENTOS Y ESTADOS
# ══════════════════════════════════════════════════

@app.route("/api/orders", methods=["POST"])
def create_order():
    """Registra un nuevo pedido en la BD y valida que no haya items sin stock."""
    data = request.get_json() or {}

    client_name = data.get("name", "").strip()
    client_phone = data.get("phone", "").strip()
    card_occasion = data.get("card_occasion", "Sin especificar")
    card_message = data.get("card_message", "").strip()
    payment_method = data.get("payment_method", "efectivo")
    notes = data.get("notes", "").strip()
    items = data.get("items", [])

    if not client_name or not client_phone or not items:
        return jsonify({"error": "Faltan datos obligatorios para el pedido"}), 400

    conn = get_db()
    total_price = 0
    detailed_items = []

    for item in items:
        pid = item.get("id")
        qty = int(item.get("qty", 1))
        row = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
        if row:
            # Validar stock en el momento del pedido
            if row["in_stock"] == 0:
                conn.close()
                return jsonify({"error": f"El producto '{row['name']}' se encuentra actualmente sin stock."}), 400

            subtotal = row["price"] * qty
            total_price += subtotal
            detailed_items.append({
                "id": pid,
                "name": row["name"],
                "price": row["price"],
                "qty": qty,
                "subtotal": subtotal
            })

    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (
            client_name, client_phone, card_occasion, card_message,
            payment_method, notes, items_json, total_price, created_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
    """, (
        client_name, client_phone, card_occasion, card_message,
        payment_method, notes, json.dumps(detailed_items, ensure_ascii=False),
        total_price, created_at
    ))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Construir mensaje tipo ticket profesional (sin asteriscos, sin emojis y sin caracteres que causen errores)
    def clean_for_wa(text):
        if not text:
            return ""
        t = str(text).replace("*", "").replace("_", "").replace("`", "").replace("~", "")
        # Filtrar caracteres mayores a 0x2000 (emojis y simbolos extraños que rompen Windows WhatsApp)
        cleaned = "".join(c for c in t if ord(c) < 0x2000)
        import re
        return re.sub(r" +", " ", cleaned).strip()

    def fmt_money(val):
        return f"{val:,.0f}".replace(",", ".")

    payment_desc = "Transferencia bancaria" if payment_method == "transferencia" else "Efectivo al retirar"

    lines = [
        "========================================",
        "       GOMILANDIA - NUEVO PEDIDO",
        "========================================",
        "",
        "DATOS DEL PEDIDO:",
        f"  Nro. de Pedido: #{order_id}",
        f"  Fecha: {created_at}",
        f"  Cliente: {clean_for_wa(client_name)}",
        f"  Telefono: {clean_for_wa(client_phone)}",
        "",
        "----------------------------------------",
        "DETALLE DE PRODUCTOS:",
        "----------------------------------------"
    ]

    for it in detailed_items:
        name = clean_for_wa(it["name"])
        qty = it.get("qty", 1)
        if qty > 1:
            lines.append(f"  - {name} x{qty}: ${fmt_money(it['subtotal'])} (${fmt_money(it['price'])} c/u)")
        else:
            lines.append(f"  - {name} x{qty}: ${fmt_money(it['subtotal'])}")

    lines.extend([
        "",
        "----------------------------------------",
        f"TOTAL A PAGAR: ${fmt_money(total_price)}",
        "----------------------------------------",
        "",
        "DATOS DE ENTREGA Y PAGO:",
        f"  Forma de pago: {payment_desc}"
    ])

    if card_occasion:
        lines.append(f"  Tarjeta de regalo: {clean_for_wa(card_occasion)}")

    if card_message:
        lines.append(f'  Mensaje para tarjeta: "{clean_for_wa(card_message)}"')

    if notes:
        lines.append(f'  Aclaraciones: "{clean_for_wa(notes)}"')

    lines.extend([
        "",
        "========================================",
        "Coordinamos retiro y entrega por aca.",
        "Muchas gracias por tu compra!",
        "========================================"
    ])

    wa_msg = "\n".join(lines)

    import urllib.parse
    encoded_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(wa_msg)}"

    return jsonify({
        "success": True,
        "order_id": order_id,
        "total": total_price,
        "whatsapp_url": encoded_url
    })


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Retorna historial de ventas para el panel de administración."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    conn = get_db()
    rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()

    orders_list = []
    for r in rows:
        d = dict(r)
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        orders_list.append(d)

    return jsonify(orders_list)


@app.route("/api/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    """Permite al admin cambiar el estado de un pedido (pendiente, entregado, cancelado)."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json() or {}
    new_status = data.get("status", "pendiente").lower()

    if new_status not in ["pendiente", "entregado", "cancelado"]:
        return jsonify({"error": "Estado inválido"}), 400

    conn = get_db()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "status": new_status, "message": "Estado actualizado"})


@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    """Permite al admin eliminar un pedido (por ejemplo, pedidos de prueba o cancelados)."""
    if not session.get("is_admin"):
        return jsonify({"error": "No autorizado"}), 401

    conn = get_db()
    conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Pedido eliminado correctamente"})


# ══════════════════════════════════════════════════
# APIS PARA AUTENTICACIÓN ADMIN
# ══════════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def login():
    """Autenticación del panel de administración."""
    data = request.get_json() or {}
    user = data.get("user", "").strip()
    pwd = data.get("password", "").strip()

    if user == ADMIN_USER and pwd == ADMIN_PASS:
        session["is_admin"] = True
        return jsonify({"success": True, "message": "Bienvenido al Panel Administrador"})
    return jsonify({"error": "Usuario o contraseña incorrectos"}), 401


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("is_admin", None)
    return jsonify({"success": True})


@app.route("/api/auth_status", methods=["GET"])
def auth_status():
    return jsonify({"is_admin": bool(session.get("is_admin"))})


# ══════════════════════════════════════════════════
# INICIO DE LA APLICACIÓN
# ══════════════════════════════════════════════════

if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("[+] SERVIDOR GOMILANDIA INICIADO EXITOSAMENTE")
    print("[*] Tienda Pública:      http://127.0.0.1:5000")
    print("[*] Panel Administrador: http://127.0.0.1:5000/admin")
    print("[*] Credenciales:        Usuario: gomilandia  |  Clave: gomitas2026")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
