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

@app.route('/sign-up', methods=['POST'])
def signup():
    data            = request.get_json()
    name            = data.get('username')
    email           = data.get('email')
    password        = data.get('password')
    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (user_name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
    mysql.connection.commit()
    cur.close()

    response = {
        'status': True,
        'message': 'User created successfully'
    }
    return jsonify(response), 201

@app.route('/sign-in', methods=['POST'])
def signin():
    data            = request.get_json()
    email           = data.get('email')
    password        = data.get('password')

    cur = mysql.connection.cursor()
    cur.execute("SELECT user_name, email, password FROM users WHERE email=%s",  (email,))
    mysql.connection.commit()
    user = cur.fetchone()
    cur.close()

    if(user):
        if (check_password_hash(user[2], password)):
            response = {
                'status': True,
                'message': "Success Login"
            }        
        else:
            response = {
                'status': False,
                'message': "Email or Password doesn't match"
            }
    else:
        response = {
                'status': False,
                'message': "Email or Password doesn't exist"
            }
        
    return jsonify(response), 201
    

if __name__ == '__main__':
    app.run()