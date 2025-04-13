from flask import Flask, jsonify, request, render_template
import random
import os
import time
from twilio.rest import Client

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token') 
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
import random
import os
from twilio.rest import Client
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder=".", static_url_path="", template_folder=".")

# OTP storage with expiration (production: replace with database)
otp_storage = {}
rate_limit = {}  # Track failed attempts

# Configuration
OTP_EXPIRY = 300  # 5 minutes in seconds
MAX_ATTEMPTS = 3  # Max verification attempts
CORS(app)

# Sample database (we'll replace this with a proper database later)
products = {
    "pulses": [
        {
            "id": 1,
            "name": "Moong Dal",
            "price": 140,
            "quantity": "1kg",
            "image": "https://images.pexels.com/photos/4110476/pexels-photo-4110476.jpeg",
        },
        {
            "id": 2,
            "name": "Toor Dal",
            "price": 130,
            "quantity": "1kg",
            "image": "https://images.pexels.com/photos/4110465/pexels-photo-4110465.jpeg",
        },
        {
            "id": 3,
            "name": "Chana Dal",
            "price": 110,
            "quantity": "1kg",
            "image": "https://images.pexels.com/photos/4110470/pexels-photo-4110470.jpeg",
        },
    ],
    "snacks": [
        {
            "id": 4,
            "name": "Lays Classic",
            "price": 40,
            "quantity": "Large pack",
            "image": "https://images.pexels.com/photos/5945754/pexels-photo-5945754.jpeg",
        },
        {
            "id": 5,
            "name": "Kurkure",
            "price": 30,
            "quantity": "Large pack",
            "image": "https://images.pexels.com/photos/1618914/pexels-photo-1618914.jpeg",
        },
    ],
    "stationery": [
        {
            "id": 6,
            "name": "Premium Pencil Set",
            "price": 50,
            "quantity": "Pack of 10",
            "image": "https://images.pexels.com/photos/6444/pencil-typography-black-design.jpg",
        },
        {
            "id": 7,
            "name": "Ruled Notebook",
            "price": 60,
            "quantity": "200 pages",
            "image": "https://images.pexels.com/photos/4226896/pexels-photo-4226896.jpeg",
        },
        {
            "id": 8,
            "name": "Ball Point Pen Set",
            "price": 45,
            "quantity": "Pack of 5",
            "image": "https://images.pexels.com/photos/4226805/pexels-photo-4226805.jpeg",
        },
    ],
    "crockery": [
        {
            "id": 9,
            "name": "Steel Plate Set",
            "price": 450,
            "quantity": "Set of 6",
            "image": "https://images.pexels.com/photos/6270541/pexels-photo-6270541.jpeg",
        },
        {
            "id": 10,
            "name": "Steel Glass Set",
            "price": 299,
            "quantity": "Set of 6",
            "image": "https://images.pexels.com/photos/6270543/pexels-photo-6270543.jpeg",
        },
    ],
    "bathroom": [
        {
            "id": 11,
            "name": "Cotton Bath Towel",
            "price": 299,
            "quantity": "Large Size",
            "image": "https://images.pexels.com/photos/3490355/pexels-photo-3490355.jpeg",
        },
        {
            "id": 12,
            "name": "Bathroom Accessories Set",
            "price": 599,
            "quantity": "Complete Set",
            "image": "https://images.pexels.com/photos/3735149/pexels-photo-3735149.jpeg",
        },
    ],
}

# Initialize empty lists for cart and orders
cart_items = []
orders = []


# Cart management functions
def get_cart():
    return cart_items


def add_to_cart(item):
    cart_items.append(item)
    return cart_items


def remove_from_cart(item_id):
    global cart_items
    cart_items = [item for item in cart_items if item["id"] != item_id]
    return cart_items


def clear_cart():
    global cart_items
    cart_items = []
    return cart_items


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/cart.html")
def cart():
    return app.send_static_file("cart.html")


@app.route("/api/products")
def get_products():
    category = request.args.get("category", None)
    if category and category in products:
        return jsonify(products[category])
    return jsonify(products)


@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    phone = data.get("phone")
    
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    # Clear previous OTP if exists
    if phone in otp_storage:
        del otp_storage[phone]

    otp = str(random.randint(100000, 999999))
    otp_storage[phone] = {
        "code": otp,
        "timestamp": time.time(),
        "attempts": 0
    }
    
    # For testing without Twilio credentials
    # For production, do not return the OTP in the response
    return jsonify({"message": "OTP sent successfully"})

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    phone = data.get("phone")
    otp = data.get("otp")
    
    if not phone or not otp:
        return jsonify({"error": "Phone and OTP are required"}), 400

    # Check if OTP exists and is not expired
    if phone not in otp_storage:
        return jsonify({"error": "OTP expired or not requested"}), 401
        
    stored_data = otp_storage[phone]
    
    # Check expiration
    if time.time() - stored_data["timestamp"] > OTP_EXPIRY:
        del otp_storage[phone]
        return jsonify({"error": "OTP expired"}), 401
        
    # Check rate limiting
    if stored_data["attempts"] >= MAX_ATTEMPTS:
        return jsonify({"error": "Too many attempts"}), 429
        
    # Verify OTP
    if stored_data["code"] == otp:
        del otp_storage[phone]
        return jsonify({"message": "OTP verified successfully"})
    else:
        otp_storage[phone]["attempts"] += 1
        remaining = MAX_ATTEMPTS - otp_storage[phone]["attempts"]
        return jsonify({
            "error": "Invalid OTP",
            "remaining_attempts": remaining
        }), 401

@app.route("/product/<int:product_id>")
def product_details(product_id):
    # Search through all categories for the product
    for category in products.values():
        for product in category:
            if product["id"] == product_id:
                return render_template("product_details.html", product=product)
    return "Product not found", 404

# Temporary test route
@app.route("/test_product")
def test_product():
    return str([p["id"] for category in products.values() for p in category])

@app.route("/api/cart", methods=["GET", "POST", "DELETE"])
def manage_cart():
    if request.method == "GET":
        return jsonify(get_cart())
    elif request.method == "POST":
        item = request.json
        updated_cart = add_to_cart(item)
        return jsonify({"message": "Item added to cart", "cart": updated_cart})
    elif request.method == "DELETE":
        item_id = request.args.get("id")
        if item_id:
            updated_cart = remove_from_cart(int(item_id))
        else:
            updated_cart = clear_cart()
        return jsonify({"message": "Cart updated", "cart": updated_cart})


@app.route("/api/checkout", methods=["POST"])
def checkout():
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    order = {
        "id": len(orders) + 1,
        "items": cart_items.copy(),
        "total": sum(item["price"] for item in cart_items),
        "date": datetime.now().isoformat(),
        "status": "pending",
    }
    orders.append(order)
    clear_cart()
    return jsonify({"message": "Order placed successfully", "order": order})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
