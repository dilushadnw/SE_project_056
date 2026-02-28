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

@app.route('/items')
def items():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM items_6")
            all_items = cursor.fetchall()
    finally:
        connection.close()
    return render_template('items.html', items=all_items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_code = request.form['item_code']
        name = request.form['name']
        category = request.form['category']
        quantity = request.form['quantity']

        if not item_code.startswith('ict2023056-'):
            flash("Error: Item code must start with 'ict2023056-'")
            return redirect(url_for('add_item'))
        
        if int(quantity) < 0:
            flash("Error: Quantity must be 0 or greater.")
            return redirect(url_for('add_item'))

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO items_6 (item_code, name, category, quantity) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (item_code, name, category, quantity))
            connection.commit()
            flash("Item added successfully!")
            return redirect(url_for('items'))
        except pymysql.err.IntegrityError:
            flash("Error: This Item Code already exists! Please use a unique code.")
            return redirect(url_for('add_item'))
        finally:
            connection.close()

    return render_template('add.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_item(id):
    connection = get_db_connection()
    
    if request.method == 'POST':
        new_quantity = request.form['quantity']

        if int(new_quantity) < 0:
            flash("Error: Quantity cannot be less than 0.")
            return redirect(url_for('update_item', id=id))

        try:
            with connection.cursor() as cursor:
                sql = "UPDATE items_6 SET quantity = %s WHERE id = %s"
                cursor.execute(sql, (new_quantity, id))
            connection.commit()
            flash("Quantity updated successfully!")
            return redirect(url_for('items'))
        finally:
            connection.close()
    else:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM items_6 WHERE id = %s", (id,))
                item = cursor.fetchone()
        finally:
            connection.close()
        return render_template('update.html', item=item)

@app.route('/delete/<int:id>')
def delete_item(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM items_6 WHERE id = %s", (id,))
        connection.commit()
        flash("Item deleted successfully!")
    finally:
        connection.close()
    return redirect(url_for('items'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    items = []
    
    if query:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                search_term = f"%{query}%"
                sql = "SELECT * FROM items_6 WHERE name LIKE %s OR category LIKE %s"
                cursor.execute(sql, (search_term, search_term))
                items = cursor.fetchall()
        finally:
            connection.close()
            
    return render_template('search.html', items=items, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
