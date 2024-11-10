from flask import Flask, render_template, request, redirect, url_for,flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="1234",  
        database="airline_db"
    )

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are for admin
        if username == 'i_am_admin' and password == 'admin':  
            return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

        # Check credentials in the database for other users
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        # If user is found, login to user dashboard
        if user:
            session['user'] = user  # Store user details in session
            return redirect(url_for('dashboard'))  # Redirect to user dashboard
        else:
            return "Invalid credentials"  # Invalid credentials message

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = 'user'  # Default user type is 'user'
        
        # Insert new user into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "Username already exists. Please choose a different one."
        
        cursor.execute("INSERT INTO users (username, password, user_type) VALUES (%s, %s, %s)", 
                       (username, password, user_type))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html')

@app.route('/book_flight', methods=['GET', 'POST'])
def book_flight():
    if request.method == 'POST':
        flight_id = request.form['flight_id']
        passenger_name = request.form['passenger_name']
        
        # Insert booking into database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bookings (flight_id, passenger_name) VALUES (%s, %s)", (flight_id, passenger_name))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))
    
    # Fetch available flights
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    conn.close()

    return render_template('book_flight.html', flights=flights)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user session data
    return redirect(url_for('login'))  # Redirect to login page


@app.route('/view_flights', methods=['GET', 'POST'])
def view_flights():
    search_query = ""
    flights = []

    if request.method == 'POST':
        search_query = request.form.get('search_query')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flights WHERE flight_name LIKE %s OR departure LIKE %s OR arrival LIKE %s", 
                       ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
        flights = cursor.fetchall()
        conn.close()
    else:
        # Fetch all flights
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flights")
        flights = cursor.fetchall()
        conn.close()

    return render_template('view_flights.html', flights=flights, search_query=search_query)

@app.route('/admin_dashboard')
def admin_dashboard():

    # Fetch all flights and bookings
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    cursor.execute("SELECT * FROM bookings")
    bookings = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', flights=flights, bookings=bookings)

@app.route('/admin_add_flight', methods=['GET', 'POST'])
def admin_add_flight():

    if request.method == 'POST':
        flight_name = request.form['flight_name']
        departure = request.form['departure']
        arrival = request.form['arrival']
        
        # Insert new flight into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flights (flight_name, departure, arrival) VALUES (%s, %s, %s)", (flight_name, departure, arrival))
        conn.commit()
        conn.close()

        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_add_flight.html')

if __name__ == '__main__':
    app.run(debug=True)
