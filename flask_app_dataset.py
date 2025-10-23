import os
import dataset
from flask import Flask, make_response, jsonify, request

'''
The most simpliest way...
'''
app = Flask(__name__)
db = dataset.connect('sqlite:///books.db')

table = db['books']

def fetch_db(book_id):
    return table.find_one(book_id=book_id)

def fetch_db_all():
    books = []
    for book in table:
        books.append(book)
    return books

@app.route('/api/db_populate', methods=['GET'])
def db_populate():
    table.insert({
        "book_id": "1",
        "name": "The Familiar Spirit",
        "author": "Butler, D.J. & Ritchey, Aaron Michael"
    })
    table.insert({
        "book_id": "2",
        "name": "Futility",
        "author": "Onoh, Nuzo"
    })
    return make_response(jsonify(fetch_db_all()), 200)

@app.get('/')
def api_root():
    return {
        "name": "Python REST API Example",
        "summary": "This is a simple REST API architecture with SQLite data",
        "implements": "GET, POST (/api/books) and GET, PUT, DELETE methods (/api/books/<id>)",
        "initialize DB": "GET /api/db_populate",
        "version": "1.0.0"
    }

@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == "GET":
        return make_response(jsonify(fetch_db_all()), 200)
    elif request.method == 'POST':
        content = request.json
        book_id = content['book_id']
        table.insert(content)
        return make_response(jsonify(fetch_db(book_id)), 201)

@app.route('/api/books/<book_id>', methods=['GET', 'PUT', 'DELETE'])
def api_each_book(book_id):
    if request.method == "GET":
        book_obj = fetch_db(book_id)
        if book_obj:
            return make_response(jsonify(book_obj), 200)
        else:
            return make_response(jsonify(book_obj), 404)
    elif request.method == "PUT":
        content = request.json
        table.update(content, ['book_id'])
        book_obj = fetch_db(book_id)
        return make_response(jsonify(book_obj), 200)
    elif request.method == "DELETE":
        table.delete(id=book_id)
        return make_response(jsonify({}), 204)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
