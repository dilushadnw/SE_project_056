import os
import socket
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "dilusha_secret_key"

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    student_id = "ICT2023056"
    hostname = socket.gethostname()
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM items_6")
            result = cursor.fetchone()
            total_items = result['total'] if result else 0
    finally:
        connection.close()
        
    return render_template('index.html', student_id=student_id, hostname=hostname, total_items=total_items)

# 2. List Items Page (Route: /items)
@app.route('/items')
def items():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Database eken items_6 table eke thiyena okkoma data gannawa
            cursor.execute("SELECT * FROM items_6")
            all_items = cursor.fetchall()
    finally:
        connection.close()
    return render_template('items.html', items=all_items)
# 3. Add Item Page (Route: /add)
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_code = request.form['item_code']
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']

        # Validations
        if not item_code.startswith('ict2023056-'):
            flash("Error: Item Code eka 'ict2023056-' walin patan ganna onema nisa hariyata danna!")
            return redirect(url_for('add_item'))
        
        if int(quantity) < 0:
            flash("Error: Quantity eka 0 ta wada wadi hari samana hari wenna one!")
            return redirect(url_for('add_item'))

        # Database ekata data eka save kirima
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Parameterized query ekak use karanne SQL injection nawaththanna
                sql = "INSERT INTO items_6 (item_code, name, category, quantity) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (item_code, name, category, quantity))
            connection.commit()
            flash("Item eka lassanata add una!")
            return redirect(url_for('items'))
        except pymysql.err.IntegrityError:
            # Duplicate item code ekak awoth me error eka pennanawa
            flash("Oops! Oya Item Code eka kalin use karala thiyenne. Karunakara wena code ekak danna.")
            return redirect(url_for('add_item'))
        finally:
            connection.close()

    return render_template('add.html')
# 4. Update Quantity Page (Route: /update/<id>)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_item(id):
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_quantity = request.form['quantity']

        # Validation: Quantity eka 0 ta wada adu wenna baha
        if int(new_quantity) < 0:
            flash("Error: Quantity eka 0 ta wada adu wenna baha!")
            return redirect(url_for('update_item', id=id))

        # Database eke quantity eka update kirima (Parameterized query)
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE items_6 SET quantity = %s WHERE id = %s"
                cursor.execute(sql, (new_quantity, id))
            connection.commit()
            flash("Quantity eka hariyata update una!")
            return redirect(url_for('items'))
        finally:
            connection.close()
    else:
        # GET request eke form eka pennanna kalin dan thiyena data eka gannawa
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM items_6 WHERE id = %s", (id,))
                item = cursor.fetchone()
        finally:
            connection.close()
        return render_template('update.html', item=item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

