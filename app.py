from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from flask_cors import CORS
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

app = Flask(__name__)

CORS(app)

client = MongoClient(os.environ.get("MONGODB_URI"))

db = client.library_app
library = db.library
queue = db.queue
favorites = db.favorites
browse = db.browse

relevant_keys = ['image', 'title', 'author', 'description', 'category', 'pageCount', 'publisher', 'publishedDate']

# search for a book from GoogleAPI
@app.route("/")
def index():
    search = request.args.get('input')
    if not search:
        return "Enter a valid search!"

    max_results = '20'
    # get request to Google Books API
    url = 'https://www.googleapis.com/books/v1/volumes'
    param = search
    querystring = {'q': param, 'maxResults': max_results,
                   'orderBy': 'relevance', 'key': os.environ.get('GOOGLE_API_KEY')}

    # query results
    response = requests.get(url, params=querystring)
    data = response.json()
    return data

 # add to browsed collection
@app.route("/browse", methods=['POST'])
def add_browse():
    book = request.json
    parse_data(book)
    
    title = book['title']
    in_browsed = list(browse.find({'title': title}))
    if len(in_browsed) == 0:
        browse.insert_one(book)
        return jsonify("")
    else:
        return jsonify("")

 # add to books collection
@app.route("/library", methods=['POST'])
def add_library():
    book = request.json
    parse_data(book)
    
    title = book['title']
    in_library = list(library.find({'result.title': title}))
    if len(in_library) == 0:
        library.insert_one(book)
        return jsonify("This book has been added to your Bookshelf.")
    else:
        return jsonify("This book is already on your Bookshelf.")
    
 # add to queue collection
@app.route("/queue", methods=['POST'])
def add_queue():
    book = request.json
    parse_data(book)
    
    title = book['title']
    in_library = list(library.find({'result.title': title}))
    if len(in_library) == 0:
        bool = list(queue.find({'result.title': title}))
        if len(bool) == 0:
            queue.insert_one(book)
            return jsonify("This book has been added to Queue.")
    else:
        return jsonify("This book is already in either your Queue or on your Bookshelf.")
    
 # add to favorites collection
@app.route("/favorites", methods=['POST'])
def add_favorites():
    book = request.json

    title = book['title']
    in_favorites = list(favorites.find({'title': title}))
    if len(in_favorites) == 0:
        favorites.insert_one(book)
        return jsonify("This book has been added to Favorites.")
    else:
        return jsonify("This book is already in Favorites.")

def parse_data(book):
    contained_keys = []
    for key, value in book.items():
        contained_keys.append(key)
    null_values = list((Counter(relevant_keys) - Counter(contained_keys)).elements())
    for item in null_values:
        book[item] = None
    print(book)
    return book

# route to display all collections
@app.route('/display/<name>', methods=['GET'])
def display(name):
    if name == 'library':
        display_browsed = library.find().sort('result.title', 1)
    elif name == 'browse':
        display_browsed = browse.find().sort('_id', -1).limit(14)
    elif name == 'favorites':
        display_browsed = favorites.find().sort('result.title', 1)
    else:
        display_browsed = queue.find()
    
    data_json = []
    for data in display_browsed:
        image = data['image']
        title = data['title']
        author = data['author']
        description = data['description']
        category = data['category']
        pageCount = data['pageCount']
        published_date = data['publishedDate']
        publisher = data['publisher']
        
        data_dict = {
            'image': image,
            'title': title,
            'author': author,
            'description': description,
            'category': category,
            'pageCount': pageCount,
            'publishedDate': published_date,
            'publisher': publisher,
        }
        data_json.append(data_dict)
    return data_json

# reset the collections to empty
@app.route('/reset_db', methods=['POST'])
def reset_db():
    book = request.json
    collection = db[book]
    if collection is not None:
        collection.delete_many({})
        return jsonify("")
    else:
        return jsonify("No Collections match")

# delete individual books from collections
@app.route('/delete_db/<title>', methods=['POST'])
def delete_db(title):
    results = request.args.get('title')
    collection = db[title]
    if collection is not None:
        collection.delete_one({'title': results})
        return jsonify("")
    else:
        return jsonify("No Collections match")
    
# switch items between library and queue collections
@app.route('/switch_db/<title>', methods=['POST'])
def switch_db(title):
    results = request.args.get('title')
    if title == "queue":
        in_queue = list(queue.find({'title': results}))
        queue.delete_one({'title': results})
        in_library = list(library.find({'title': title}))
        if len(in_library) == 0:
            library.insert_one(in_queue[0])
            return jsonify("This book has been added to your Bookshelf.")
        else:
            return jsonify("This book is already on your Bookshelf.")
    elif title == "library":
        in_library = list(library.find({'title': results}))
        library.delete_one({'title': results})
        in_queue = list(queue.find({'title': title}))
        if len(in_queue) == 0:
            queue.insert_one(in_library[0])
            return jsonify("This book has been added to your Queue.")
        else:
            return jsonify("This book is already on your Queue.")
    else:
        return jsonify("No Collections match")

if __name__ == "__main__":
    app.run(host='0.0.0.0')