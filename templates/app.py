from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Function to create a connection to the SQLite database
def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('userdata.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            email TEXT NOT NULL,
                            phone TEXT,
                            dob TEXT,
                            gender TEXT
                        )''')
        conn.commit()
        print("Database connection established.")
    except Exception as e:
        print("Error creating table:", e)
    return conn

# Function to insert or update user data in the database
def insert_or_update_user(user_data):
    """
    Insert or update user data in the database.
    """
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            # Check if the user already exists
            cursor.execute("SELECT * FROM users WHERE username=?", (user_data['username'],))
            if cursor.fetchone():
                # Update existing user
                cursor.execute("UPDATE users SET email=?, phone=?, dob=?, gender=? WHERE username=?", 
                                (user_data['email'], user_data['phone'], user_data['dob'], user_data['gender'], user_data['username']))
            else:
                # Insert new user
                cursor.execute("INSERT INTO users (username, email, phone, dob, gender) VALUES (?, ?, ?, ?, ?)", 
                                (user_data['username'], user_data['email'], user_data['phone'], user_data['dob'], user_data['gender']))

            conn.commit()

            # Check if the commit was successful
            if conn.total_changes > 0:
                print("User data inserted successfully.")
                return True
            else:
                print("No changes were made to the database.")
                return False

        except Exception as e:
            print("Error inserting or updating user data:", e)
            return False
        finally:
            conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return False

# Route to render the HTML form
@app.route('/')
def index():
    return render_template('index.html', registered=False)

# Route to handle form submission and store data in the database
@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    dob = request.form['dob']
    gender = request.form['gender']

    user_data = {
        'username': username,
        'email': email,
        'phone': phone,
        'dob': dob,
        'gender': gender
    }

    print("Received user data:", user_data)

    # Insert or update user data
    if insert_or_update_user(user_data):
        return render_template('index.html', registered=True)
    else:
        return render_template('index.html', registered=False)

if __name__ == '__main__':
    if not os.path.exists('userdata.db'):
        create_connection()
    app.run(debug=True)
