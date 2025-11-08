from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bloomhaven_secret_key_2023'

# Configure CORS to allow ALL origins (including file://)
CORS(app, origins=["*"], supports_credentials=True)

# Serve static images
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Database setup
def init_db():
    conn = sqlite3.connect('bloomhaven.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT,
            description TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plant_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (plant_id) REFERENCES plants (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            delivery_address TEXT NOT NULL,
            delivery_option TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample plants if they don't exist
    c.execute("SELECT COUNT(*) FROM plants")
    if c.fetchone()[0] == 0:
        plants = [
            # Flowering plants (15)
            (1, 'Rose', 'flowering', 12.99, '/images/flowering/rose.jpg', 'Classic flowering shrub with fragrant blooms'),
            (2, 'Tulip', 'flowering', 8.99, '/images/flowering/tulip.jpg', 'Spring-blooming perennial with colorful cup-shaped flowers'),
            (3, 'Sunflower', 'flowering', 6.99, '/images/flowering/sunflower.jpg', 'Tall annual with large yellow flower heads'),
            (4, 'Lavender', 'flowering', 10.99, '/images/flowering/lavender.jpg', 'Fragrant purple flowers with calming scent'),
            (5, 'Orchid', 'flowering', 24.99, '/images/flowering/orchid.jpg', 'Exotic flowering plant with intricate blooms'),
            (6, 'Daisy', 'flowering', 7.99, '/images/flowering/daisy.jpg', 'Cheerful perennial with white petals and yellow center'),
            (7, 'Lily', 'flowering', 14.99, '/images/flowering/lily.jpg', 'Elegant trumpet-shaped flowers in various colors'),
            (8, 'Marigold', 'flowering', 5.99, '/images/flowering/marigold.jpg', 'Bright orange or yellow flowers, great for borders'),
            (9, 'Hibiscus', 'flowering', 16.99, '/images/flowering/hibiscus.jpg', 'Tropical shrub with large, colorful flowers'),
            (10, 'Peony', 'flowering', 18.99, '/images/flowering/peony.jpg', 'Lush, fragrant blooms in spring'),
            (11, 'Dahlia', 'flowering', 13.99, '/images/flowering/dahlia.jpg', 'Vibrant flowers with intricate petal patterns'),
            (12, 'Zinnia', 'flowering', 6.49, '/images/flowering/zinnia.jpg', 'Colorful, long-lasting summer blooms'),
            (13, 'Pansy', 'flowering', 5.49, '/images/flowering/pansy.jpg', 'Cool-weather flowers with faces'),
            (14, 'Petunia', 'flowering', 7.49, '/images/flowering/petunia.jpg', 'Trailing flowers perfect for containers'),
            (15, 'Geranium', 'flowering', 9.99, '/images/flowering/geranium.jpg', 'Classic garden plant with clusters of flowers'),
            
            # Indoor plants (15)
            (16, 'Snake Plant', 'indoor', 19.99, '/images/indoor/snake_plant.jpg', 'Hardy plant with tall, upright leaves'),
            (17, 'Spider Plant', 'indoor', 12.99, '/images/indoor/spider_plant.jpg', 'Easy-care plant with arching leaves'),
            (18, 'Peace Lily', 'indoor', 22.99, '/images/indoor/peace_lily.jpg', 'Elegant plant with white flowers'),
            (19, 'Pothos', 'indoor', 14.99, '/images/indoor/pothos.jpg', 'Trailing vine with heart-shaped leaves'),
            (20, 'ZZ Plant', 'indoor', 24.99, '/images/indoor/zz_plant.jpg', 'Low-maintenance with glossy leaves'),
            (21, 'Rubber Plant', 'indoor', 29.99, '/images/indoor/rubber_plant.jpg', 'Striking plant with large, dark leaves'),
            (22, 'Monstera', 'indoor', 34.99, '/images/indoor/monstera.jpg', 'Tropical plant with split leaves'),
            (23, 'Fiddle Leaf Fig', 'indoor', 39.99, '/images/indoor/fiddle_leaf.jpg', 'Popular plant with large, violin-shaped leaves'),
            (24, 'Chinese Money Plant', 'indoor', 16.99, '/images/indoor/chinese_money.jpg', 'Unique plant with round, coin-like leaves'),
            (25, 'Aloe Vera', 'indoor', 11.99, '/images/indoor/aloe_vera.jpg', 'Succulent with healing properties'),
            (26, 'Jade Plant', 'indoor', 13.99, '/images/indoor/jade_plant.jpg', 'Succulent with thick, oval leaves'),
            (27, 'Boston Fern', 'indoor', 18.99, '/images/indoor/boston_fern.jpg', 'Lush fern with arching fronds'),
            (28, 'Philodendron', 'indoor', 17.99, '/images/indoor/philodendron.jpg', 'Versatile plant with heart-shaped leaves'),
            (29, 'Calathea', 'indoor', 21.99, '/images/indoor/calathea.jpg', 'Ornamental plant with patterned leaves'),
            (30, 'String of Pearls', 'indoor', 15.99, '/images/indoor/string_of_pearls.jpg', 'Trailing succulent with bead-like leaves'),
            
            # Vegetable plants (20)
            (31, 'Tomato', 'vegetable', 4.99, '/images/vegetables/tomato.jpg', 'Versatile fruit for salads, sauces, and more'),
            (32, 'Bell Pepper', 'vegetable', 3.99, '/images/vegetables/bell_pepper.jpg', 'Sweet peppers in various colors'),
            (33, 'Cucumber', 'vegetable', 3.49, '/images/vegetables/cucumber.jpg', 'Refreshing vegetable for salads and pickling'),
            (34, 'Carrot', 'vegetable', 2.99, '/images/vegetables/carrot.jpg', 'Sweet root vegetable, rich in vitamin A'),
            (35, 'Lettuce', 'vegetable', 2.49, '/images/vegetables/lettuce.jpg', 'Leafy green for salads and sandwiches'),
            (36, 'Spinach', 'vegetable', 2.79, '/images/vegetables/spinach.jpg', 'Nutrient-rich leafy green'),
            (37, 'Broccoli', 'vegetable', 3.29, '/images/vegetables/broccoli.jpg', 'Green vegetable with tree-like heads'),
            (38, 'Cauliflower', 'vegetable', 3.59, '/images/vegetables/cauliflower.jpg', 'Versatile vegetable with white florets'),
            (39, 'Zucchini', 'vegetable', 2.89, '/images/vegetables/zucchini.jpg', 'Summer squash with mild flavor'),
            (40, 'Eggplant', 'vegetable', 3.79, '/images/vegetables/eggplant.jpg', 'Purple vegetable for various dishes'),
            (41, 'Green Beans', 'vegetable', 2.69, '/images/vegetables/green_beans.jpg', 'Crisp pods, great steamed or in casseroles'),
            (42, 'Radish', 'vegetable', 1.99, '/images/vegetables/radish.jpg', 'Peppery root vegetable, grows quickly'),
            (43, 'Kale', 'vegetable', 2.89, '/images/vegetables/kale.jpg', 'Nutrient-dense leafy green'),
            (44, 'Swiss Chard', 'vegetable', 2.79, '/images/vegetables/swiss_chard.jpg', 'Colorful leafy green with colorful stems'),
            (45, 'Beets', 'vegetable', 2.99, '/images/vegetables/beets.jpg', 'Sweet root vegetable, both roots and greens edible'),
            (46, 'Onion', 'vegetable', 2.49, '/images/vegetables/onion.jpg', 'Essential cooking vegetable with pungent flavor'),
            (47, 'Garlic', 'vegetable', 3.19, '/images/vegetables/garlic.jpg', 'Flavorful bulb for cooking and health benefits'),
            (48, 'Potato', 'vegetable', 2.29, '/images/vegetables/potato.jpg', 'Versatile tuber, staple food worldwide'),
            (49, 'Sweet Potato', 'vegetable', 3.49, '/images/vegetables/sweet_potato.jpg', 'Nutritious tuber with sweet flavor'),
            (50, 'Pumpkin', 'vegetable', 5.99, '/images/vegetables/pumpkin.jpg', 'Winter squash, great for pies and decorations')
        ]
        
        c.executemany('''
            INSERT INTO plants (id, name, type, price, image, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', plants)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Helper function for database operations
def get_db_connection():
    conn = sqlite3.connect('bloomhaven.db')
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Bloom Haven Nursery API"})

@app.route('/api/plants')
def get_plants():
    conn = get_db_connection()
    plants = conn.execute('SELECT * FROM plants').fetchall()
    conn.close()
    
    # Convert to list of dictionaries and make image URLs absolute
    plants_list = []
    for plant in plants:
        plant_dict = dict(plant)
        # Make image URL absolute
        if plant_dict['image'].startswith('/'):
            plant_dict['image'] = f'http://127.0.0.1:5000{plant_dict["image"]}'
        plants_list.append(plant_dict)
    
    return jsonify(plants_list)

@app.route('/api/plants/<plant_type>')
def get_plants_by_type(plant_type):
    conn = get_db_connection()
    plants = conn.execute('SELECT * FROM plants WHERE type = ?', (plant_type,)).fetchall()
    conn.close()
    
    # Convert to list of dictionaries and make image URLs absolute
    plants_list = []
    for plant in plants:
        plant_dict = dict(plant)
        # Make image URL absolute
        if plant_dict['image'].startswith('/'):
            plant_dict['image'] = f'http://127.0.0.1:5000{plant_dict["image"]}'
        plants_list.append(plant_dict)
    
    return jsonify(plants_list)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    conn = get_db_connection()
    
    # Check if email exists
    existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (data['email'],)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create user
    conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                 (data['name'], data['email'], data['password']))
    user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.commit()
    conn.close()
    
    session['user_id'] = user_id
    return jsonify({'message': 'User created successfully', 'user_id': user_id})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                        (data['email'], data['password'])).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        return jsonify({'message': 'Login successful', 'user_id': user['id']})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/cart', methods=['GET', 'POST', 'DELETE'])
def cart():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'GET':
        cart_items = conn.execute('''
            SELECT c.*, p.name as plant_name, p.price as plant_price, p.image as plant_image
            FROM cart c 
            JOIN plants p ON c.plant_id = p.id 
            WHERE c.user_id = ?
        ''', (user_id,)).fetchall()
        conn.close()
        
        # Convert to list of dictionaries and make image URLs absolute
        cart_list = []
        for item in cart_items:
            item_dict = dict(item)
            # Make image URL absolute
            if item_dict['plant_image'].startswith('/'):
                item_dict['plant_image'] = f'http://127.0.0.1:5000{item_dict["plant_image"]}'
            cart_list.append(item_dict)
        
        return jsonify(cart_list)
    
    elif request.method == 'POST':
        data = request.json
        plant_id = data['plant_id']
        quantity = data.get('quantity', 1)
        
        # Check if item already in cart
        cart_item = conn.execute('SELECT * FROM cart WHERE user_id = ? AND plant_id = ?',
                                (user_id, plant_id)).fetchone()
        
        if cart_item:
            conn.execute('UPDATE cart SET quantity = quantity + ? WHERE user_id = ? AND plant_id = ?',
                        (quantity, user_id, plant_id))
        else:
            conn.execute('INSERT INTO cart (user_id, plant_id, quantity) VALUES (?, ?, ?)',
                        (user_id, plant_id, quantity))
        
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item added to cart'})
    
    elif request.method == 'DELETE':
        data = request.json
        plant_id = data['plant_id']
        
        conn.execute('DELETE FROM cart WHERE user_id = ? AND plant_id = ?', (user_id, plant_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Item removed from cart'})

@app.route('/api/order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    data = request.json
    conn = get_db_connection()
    
    # Get cart items and calculate total
    cart_items = conn.execute('''
        SELECT c.*, p.price 
        FROM cart c 
        JOIN plants p ON c.plant_id = p.id 
        WHERE c.user_id = ?
    ''', (user_id,)).fetchall()
    
    if not cart_items:
        conn.close()
        return jsonify({'error': 'Cart is empty'}), 400
    
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Create order
    conn.execute('''
        INSERT INTO orders (user_id, total, delivery_address, delivery_option)
        VALUES (?, ?, ?, ?)
    ''', (user_id, total, data['delivery_address'], data['delivery_option']))
    
    # Clear cart
    conn.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Order created successfully'})

if __name__ == '__main__':
    # Create images directory if it doesn't exist
    os.makedirs('images/flowering', exist_ok=True)
    os.makedirs('images/indoor', exist_ok=True)
    os.makedirs('images/vegetables', exist_ok=True)
    
    app.run(debug=True, port=5000)