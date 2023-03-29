from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'P@ssw0rd'
app.config['MYSQL_DB'] = 'sixplus'
app.config['MYSQL_PORT'] = 3309


mysql = MySQL(app)

@app.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        data = request.get_json()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')
        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (user_name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        response = {
            'status': 'success',
            'message': 'User created successfully'
        }
        return jsonify(response), 201
    
    return 'Success get'


if __name__ == '__main__':
    app.run()