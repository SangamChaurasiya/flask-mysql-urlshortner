from flask import Flask, render_template, request, redirect
from hashids import Hashids
from dotenv import load_dotenv
import mysql.connector
import os


load_dotenv()

app = Flask(__name__)

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

# Initialize the Hashids with salts
hashids = Hashids(salt='asdfghjkl', min_length=6)


# Function to connect to DB
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn


# Home route to display the form
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form['long_url']
        conn = get_db_connection()
        cursor = conn.cursor()

        # insert long url in the DB
        cursor.execute('INSERT INTO url (long_url, short_code) VALUES (%s, %s)', (long_url, ''))
        conn.commit()

        url_id = cursor.lastrowid

        # Generate unique short code
        short_code = hashids.encode(url_id)

        # Update record with short code for that long_url
        cursor.execute('UPDATE url SET short_code = %s WHERE id = %s', (short_code, url_id))

        conn.commit()

        cursor.close()

        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)
    return render_template('index.html')


# redirect from short to long_url version
@app.route('/<short_code>', methods=["GET"])
def redirect_to_long_url(short_code):
    conn = get_db_connection()
    cursor = conn.cursor()

    decoded = hashids.decode(short_code)
    if decoded:
        url_id = decoded[0]

        cursor.execute('SELECT long_url FROM url WHERE id = %s', (url_id, ))
        result = cursor.fetchone()
        cursor.close()
        conn.close()


        if result:
            return redirect(result[0])


    cursor.close()
    conn.close()

    return "URL not found", 404


if __name__ == "__main__":
    app.run(debug=True)

