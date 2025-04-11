from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__, static_folder=".", static_url_path="", template_folder=".")
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
