import os
import psycopg
from flask import Flask, request, jsonify

def get_db_connection():
    connection = psycopg.connect("postgresql://username:password@localhost:5432/dbname")
    return connection

app = Flask(__name__)

@app.get("/")
def description():
    return {
        "name": "Very Simple Python REST API Example",
	    "implements": "GET, POST (/api/user) and GET, PUT, DELETE methods (/api/user/<id>)",
        "version": "1.0.0"
    }

CREATE_USERS_TABLE = "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT);"
INSERT_USER_RETURN_ID = "INSERT INTO users (name) VALUES (%s) RETURNING id;"
SELECT_ALL_USERS = "SELECT * FROM users;"
SELECT_USER_BY_ID = "SELECT id, name FROM users WHERE id = %s;"
UPDATE_USER_BY_ID = "UPDATE users SET name = %s WHERE id = %s;"
DELETE_USER_BY_ID = "DELETE FROM users WHERE id = %s;"

conn = get_db_connection()
conn.execute(CREATE_USERS_TABLE)

# Routes:

@app.route("/api/user", methods=["GET", "POST"])
def user_post_get():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "POST":
        data = request.get_json()
        name = data["name"]
        conn.autocommit = True
        cur.execute(INSERT_USER_RETURN_ID, (name,))
        user_id = cur.fetchone()[0]
        return {"id": user_id, "name": name, "message": f"User {name} created."}, 201
    elif request.method == "GET":
        cur.execute(SELECT_ALL_USERS)
        rows = cur.fetchall()
        if rows:
            return jsonify([{"id": row[0], "name": row[1]} for row in rows])
        else:
            return jsonify({"error": f"Users not found."}), 404
    cur.close()
    conn.close()


@app.route("/api/user/<int:user_id>", methods=["GET", "PUT", "DELETE"])
def get_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute(SELECT_USER_BY_ID, (user_id,))
        row = cur.fetchone()
        if row:
            return jsonify({"id": row[0], "name": row[1]})
        else:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404
    elif request.method == "PUT":
        data = request.get_json()
        name = data["name"]
        conn.autocommit = True
        cur.execute(UPDATE_USER_BY_ID, (name, user_id))
        rc = cur.rowcount
        if rc == 0:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404
        return jsonify({"id": user_id, "name": name, "message": f"User with ID {user_id} updated."})
    elif request.method == "DELETE":
        conn.autocommit = True
        cur.execute(DELETE_USER_BY_ID, (user_id,))
        rc = cur.rowcount
        if rc == 0:
            return jsonify({"error": f"User with ID {user_id} not found."}), 404
        return jsonify({"message": f"User with ID {user_id} deleted."})
    cur.close()
    conn.close()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
