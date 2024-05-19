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
library = db.books
queue = db.queue
favorites = db.favorites
browse = db.browse

relevantKeys = ['image', 'title', 'author', 'description', 'category', 'pageCount', 'publisher', 'publishedDate']

# search for a book from GoogleAPI
@app.route("/")
def index():
    search = request.args.get('input')
    if not search:
        return "Enter a valid search!"

    maxResults = '20'
    # get request to Google Books API
    url = 'https://www.googleapis.com/books/v1/volumes'
    param = search
    querystring = {'q': param, 'maxResults': maxResults,
                   'orderBy': 'relevance', 'key': os.environ.get('GOOGLE_API_KEY')}

    # query results
    response = requests.get(url, params=querystring)
    data = response.json()
    return data

 # add to browsed collection
@app.route("/browse", methods=['POST'])
def add_browse():
    book = request.json
    parseData(book)
    
    title = book['title']
    inBrowsed = list(browse.find({'title': title}))
    if len(inBrowsed) == 0:
        browse.insert_one(book)
        return jsonify("")
    else:
        return jsonify("")

 # add to books collection
@app.route("/library", methods=['POST'])
def add_library():
    book = request.json
    parseData(book)
    
    title = book['title']
    inLibrary = list(library.find({'result.title': title}))
    if len(inLibrary) == 0:
        library.insert_one(book)
        return jsonify("This book has been added to your Bookshelf.")
    else:
        return jsonify("This book is already on your Bookshelf.")
    
 # add to queue collection
@app.route("/queue", methods=['POST'])
def add_queue():
    book = request.json
    parseData(book)
    
    title = book['title']
    inLibrary = list(library.find({'result.title': title}))
    if len(inLibrary) == 0:
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
    inFavorites = list(favorites.find({'title': title}))
    if len(inFavorites) == 0:
        favorites.insert_one(book)
        return jsonify("This book has been added to Favorites.")
    else:
        return jsonify("This book is already in Favorites.")

def parseData(book):
    containedKeys = []
    for key, value in book.items():
        containedKeys.append(key)
    nullValues = list((Counter(relevantKeys) - Counter(containedKeys)).elements())
    for item in nullValues:
        book[item] = None
    print(book)
    return book

# route to display all collections
@app.route('/display/<name>', methods=['GET'])
def display(name):
    if name == 'library':
        displayBrowsed = library.find().sort('result.title', 1)
    elif name == 'browse':
        displayBrowsed = browse.find().sort('_id', -1).limit(14)
    elif name == 'favorites':
        displayBrowsed = favorites.find().sort('result.title', 1)
    else:
        displayBrowsed = queue.find()
    
    dataJSON = []
    for data in displayBrowsed:
        image = data['image']
        title = data['title']
        author = data['author']
        description = data['description']
        category = data['category']
        pageCount = data['pageCount']
        publishedDate = data['publishedDate']
        publisher = data['publisher']
        
        dataDict = {
            'image': image,
            'title': title,
            'author': author,
            'description': description,
            'category': category,
            'pageCount': pageCount,
            'publishedDate': publishedDate,
            'publisher': publisher,
        }
        dataJSON.append(dataDict)
    return dataJSON

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
        inQueue = list(queue.find({'title': results}))
        queue.delete_one({'title': results})
        inLibrary = list(library.find({'title': title}))
        if len(inLibrary) == 0:
            library.insert_one(inQueue[0])
            return jsonify("This book has been added to your Bookshelf.")
        else:
            return jsonify("This book is already on your Bookshelf.")
    elif title == "library":
        inLibrary = list(library.find({'title': results}))
        library.delete_one({'title': results})
        inQueue = list(queue.find({'title': title}))
        if len(inQueue) == 0:
            queue.insert_one(inLibrary[0])
            return jsonify("This book has been added to your Queue.")
        else:
            return jsonify("This book is already on your Queue.")
    else:
        return jsonify("No Collections match")

if __name__ == "__main__":
    app.run(host='0.0.0.0')