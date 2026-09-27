from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)

app.secret_key = "techzone-secret-key-change-this"

DATABASE = os.path.join(os.path.dirname(__file__), "techzone.db")


# ---------------------------------------------------------
# PRODUCT DATA
# ---------------------------------------------------------

PRODUCTS = [
    (
        1,
        "Smartphone Pro",
        "Smartphones",
        49999,
        "📱",
        "Powerful smartphone with premium display and camera."
    ),
    (
        2,
        "Ultra Laptop",
        "Laptops",
        74999,
        "💻",
        "Fast laptop for study, work and entertainment."
    ),
    (
        3,
        "Wireless Headphones",
        "Headphones",
        4999,
        "🎧",
        "Wireless headphones with immersive sound."
    ),
    (
        4,
        "Smart Watch",
        "Smartwatches",
        6999,
        "⌚",
        "Smartwatch with fitness and notification features."
    ),
    (
        5,
        "Digital Camera",
        "Cameras",
        54999,
        "📷",
        "High-quality digital camera for photography."
    ),
    (
        6,
        "4K Monitor",
        "Monitors",
        29999,
        "🖥️",
        "Sharp 4K monitor for work, gaming and content."
    ),
    (
        7,
        "Gaming Keyboard",
        "Accessories",
        2499,
        "⌨️",
        "Mechanical keyboard designed for gaming."
    ),
    (
        8,
        "Wireless Mouse",
        "Accessories",
        1499,
        "🖱️",
        "Comfortable wireless mouse for everyday use."
    )
]


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Products table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            icon TEXT,
            description TEXT
        )
    """)

    # Orders table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Order items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Insert default products
    for product in PRODUCTS:

        conn.execute("""
            INSERT OR IGNORE INTO products
            (
                id,
                name,
                category,
                price,
                icon,
                description
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, product)

    conn.commit()

    conn.close()


# ---------------------------------------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------------------------------------

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for(
                    "login",
                    next=request.path
                )
            )

        return view(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------
# GLOBAL CART COUNT
# ---------------------------------------------------------

@app.context_processor
def inject_cart_count():

    cart = session.get("cart", {})

    return {
        "cart_count": sum(cart.values())
    }


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    conn = get_db()

    products = conn.execute(
        "SELECT * FROM products LIMIT 6"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        products=products
    )


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

@app.route("/products")
def products():

    category = request.args.get(
        "category",
        ""
    ).strip()

    search = request.args.get(
        "search",
        ""
    ).strip()

    conn = get_db()

    query = """
        SELECT *
        FROM products
        WHERE 1=1
    """

    params = []

    if category:

        query += """
            AND category = ?
        """

        params.append(category)

    if search:

        query += """
            AND (
                name LIKE ?
                OR category LIKE ?
            )
        """

        params.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    query += """
        ORDER BY id
    """

    product_rows = conn.execute(
        query,
        params
    ).fetchall()

    categories = conn.execute(
        """
        SELECT DISTINCT category
        FROM products
        ORDER BY category
        """
    ).fetchall()

    conn.close()

    return render_template(
        "products.html",
        products=product_rows,
        categories=categories,
        selected_category=category,
        search=search
    )


# ---------------------------------------------------------
# PRODUCT DETAILS
# ---------------------------------------------------------

@app.route("/product/<int:product_id>")
def product_details(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT *
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("products")
        )

    return render_template(
        "product_details.html",
        product=product
    )


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not email or not password:

            flash(
                "All fields are required.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password)
                )
            )

            conn.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except sqlite3.IntegrityError:

            flash(
                "Email is already registered.",
                "danger"
            )

        finally:

            conn.close()

    return render_template(
        "register.html"
    )


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                request.args.get(
                    "next"
                )
                or url_for("home")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():

    session.pop(
        "user_id",
        None
    )

    session.pop(
        "user_name",
        None
    )

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ---------------------------------------------------------
# CART
# ---------------------------------------------------------

@app.route("/cart")
def cart():

    cart_data = session.get(
        "cart",
        {}
    )

    conn = get_db()

    items = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = conn.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            """,
            (int(product_id),)
        ).fetchone()

        if product:

            subtotal = (
                product["price"]
                * quantity
            )

            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    conn.close()

    return render_template(
        "cart.html",
        items=items,
        total=total
    )


# ---------------------------------------------------------
# ADD TO CART
# ---------------------------------------------------------

@app.route(
    "/add-to-cart/<int:product_id>",
    methods=["POST"]
)
def add_to_cart(product_id):

    conn = get_db()

    product = conn.execute(
        """
        SELECT id
        FROM products
        WHERE id = ?
        """,
        (product_id,)
    ).fetchone()

    conn.close()

    if not product:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect(
            url_for("products")
        )

    cart = session.get(
        "cart",
        {}
    )

    key = str(product_id)

    quantity = int(
        request.form.get(
            "quantity",
            1
        )
    )

    cart[key] = (
        cart.get(key, 0)
        + quantity
    )

    session["cart"] = cart

    session.modified = True

    flash(
        "Product added to cart.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("products")
    )


# ---------------------------------------------------------
# UPDATE CART
# ---------------------------------------------------------

@app.route(
    "/update-cart/<int:product_id>",
    methods=["POST"]
)
def update_cart(product_id):

    quantity = max(
        0,
        int(
            request.form.get(
                "quantity",
                1
            )
        )
    )

    cart = session.get(
        "cart",
        {}
    )

    key = str(product_id)

    if quantity == 0:

        cart.pop(
            key,
            None
        )

    else:

        cart[key] = quantity

    session["cart"] = cart

    session.modified = True

    return redirect(
        url_for("cart")
    )


# ---------------------------------------------------------
# REMOVE FROM CART
# ---------------------------------------------------------

@app.route(
    "/remove-from-cart/<int:product_id>",
    methods=["POST"]
)
def remove_from_cart(product_id):

    cart = session.get(
        "cart",
        {}
    )

    cart.pop(
        str(product_id),
        None
    )

    session["cart"] = cart

    session.modified = True

    return redirect(
        url_for("cart")
    )


# ---------------------------------------------------------
# CHECKOUT
# ---------------------------------------------------------

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
@login_required
def checkout():

    cart_data = session.get(
        "cart",
        {}
    )

    if not cart_data:

        flash(
            "Your cart is empty.",
            "warning"
        )

        return redirect(
            url_for("products")
        )

    conn = get_db()

    items = []

    total = 0

    for product_id, quantity in cart_data.items():

        product = conn.execute(
            """
            SELECT *
            FROM products
            WHERE id = ?
            """,
            (int(product_id),)
        ).fetchone()

        if product:

            subtotal = (
                product["price"]
                * quantity
            )

            items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    if request.method == "POST":

        cursor = conn.execute(
            """
            INSERT INTO orders
            (
                user_id,
                total
            )
            VALUES (?, ?)
            """,
            (
                session["user_id"],
                total
            )
        )

        order_id = cursor.lastrowid

        for item in items:

            conn.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    item["product"]["id"],
                    item["quantity"],
                    item["product"]["price"]
                )
            )

        conn.commit()

        conn.close()

        session["cart"] = {}

        return redirect(
            url_for(
                "order_confirmation",
                order_id=order_id
            )
        )

    conn.close()

    return render_template(
        "checkout.html",
        items=items,
        total=total
    )


# ---------------------------------------------------------
# ORDER CONFIRMATION
# ---------------------------------------------------------

@app.route(
    "/order-confirmation/<int:order_id>"
)
@login_required
def order_confirmation(order_id):

    conn = get_db()

    order = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ?
        AND user_id = ?
        """,
        (
            order_id,
            session["user_id"]
        )
    ).fetchone()

    conn.close()

    if not order:

        flash(
            "Order not found.",
            "danger"
        )

        return redirect(
            url_for("home")
        )

    return render_template(
        "order_confirmation.html",
        order=order
    )


# ---------------------------------------------------------
# MY ORDERS
# ---------------------------------------------------------

@app.route("/orders")
@login_required
def orders():

    conn = get_db()

    user_orders = conn.execute(
        """
        SELECT *
        FROM orders
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "orders.html",
        orders=user_orders
    )


# ---------------------------------------------------------
# ADD PRODUCT
# ---------------------------------------------------------

@app.route(
    "/admin/add-product",
    methods=["GET", "POST"]
)
def add_product():

    if request.method == "POST":

        try:

            product_id = int(
                request.form["id"]
            )

            name = request.form[
                "name"
            ].strip()

            category = request.form[
                "category"
            ].strip()

            price = float(
                request.form["price"]
            )

            icon = request.form.get(
                "icon",
                "📦"
            )

            description = request.form.get(
                "description",
                ""
            ).strip()

            conn = get_db()

            conn.execute(
                """
                INSERT INTO products
                (
                    id,
                    name,
                    category,
                    price,
                    icon,
                    description
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    product_id,
                    name,
                    category,
                    price,
                    icon,
                    description
                )
            )

            conn.commit()

            conn.close()

            flash(
                "Product added successfully.",
                "success"
            )

            return redirect(
                url_for("products")
            )

        except Exception as e:

            flash(
                f"Could not add product: {e}",
                "danger"
            )

    return render_template(
        "add_product.html"
    )


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@app.route("/analytics")
def analytics():

    return render_template(
        "analytics.html"
    )


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

init_db()

if __name__ == "__main__":
    app.run(debug=True)