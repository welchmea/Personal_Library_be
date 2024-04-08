from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import certifi
import os

ENV = 'LIVE'
if ENV =='DEV':
# sets ups access to MongoDB
    mongo_db_url = os.environ.get("MONGO_DB_CONN_STRING")
if ENV == 'LIVE':
    mongo_db_url = os.environ.get('MONGODB_URI')
    
bookDB = Blueprint('database', __name__)
client = MongoClient(mongo_db_url, tlsCAFile=certifi.where())
db = client['library_app']

# reset databases
@bookDB.route('/reset_db', methods=['POST'])
def reset_db():
    book = request.json
    if book == "browse":
        db.browse.delete_many({})
        return jsonify("Browsed collection is now empty!")
    
    else:
        return jsonify("No Collections match")
# add a book to library
@bookDB.route('/add_db', methods=['POST'])
def add_db():
    book = request.json
    title = book['result']['title']
    inQueue = list(db.books.find({'result.title': title}))
    if len(inQueue) == 0:
        bool = list(db.books.find({'result.title': title}))
        if len(bool) == 0:
            db.books.insert_one(book)
            return jsonify("This book has been added to your Bookshelf.")
    else:
        return jsonify("This book is already either on your Bookshelf or in your Queue.")


# display books in library
@bookDB.route('/display_books')
def display_books():
    displayBooks = db.books.find().sort('result.title', 1)
    dataJSON = []
    for data in displayBooks:
        image = data['result']['image']
        title = data['result']['title']
        author = data['result']['author']
        dataDict = {
            'image': image,
            'title': title,
            'author': author
        }
        dataJSON.append(dataDict)
    return dataJSON


# add a book to the queue
@bookDB.route('/add_queue', methods=['POST'])
def add_queue():
    add_queue = request.json
    title = add_queue['result']['title']
    inLibrary = list(db.books.find({'result.title': title}))
    if len(inLibrary) == 0:
        bool = list(db.queue.find({'result.title': title}))
        if len(bool) == 0:
            db.queue.insert_one(add_queue)
            return jsonify("This book has been added to Queue.")
    else:
        return jsonify("This book is already in either your Queue or on your Bookshelf.")


# display books in queue
@bookDB.route('/display_queue')
def display_queue():
    displayQueue = db.queue.find()
    dataJSON = []
    for data in displayQueue:
        image = data['result']['image']
        title = data['result']['title']
        author = data['result']['author']
        dataDict = {
            'image': image,
            'title': title,
            'author': author
        }
        dataJSON.append(dataDict)
    return dataJSON


# delete a book from the queue or library
@bookDB.route('/delete_db', methods=['POST'])
def delete_db():
    delete_queue = request.json
    title = delete_queue['title']
    results = list(db.queue.find({'result.title': title}))
    if len(results) != 0:
        db.queue.delete_one({'result.title': title})
        return jsonify("You successfully deleted a book from your Queue.")
    elif len(results) == 0:
        results = list(db.favorites.find({'result.title': title}))
        if len(results) != 0:
            db.favorites.delete_one({'result.title': title})
            return jsonify("You successfully deleted a book from your Favorites.")
        elif len(results) == 0:
            results = list(db.books.find({'result.title': title}))
            if len(results) != 0:
                db.books.delete_one({'result.title': title})
                return jsonify("You have successfully deleted a book from your Bookshelf.")
    return jsonify("Oops, something went wrong.")


# switch the book from queue to library
@bookDB.route('/switch_db', methods=['POST'])
def switch_db():
    switch = request.json
    title = switch['title']
    results = list(db.queue.find({'result.title': title}))
    if len(results) != 0:
        book_results = list(db.books.find({'result.title': title}))
        if len(book_results) == 0:
            db.books.insert_one(results[0])
            db.queue.delete_one({'result.title': title})
            return jsonify("You successfully moved a book from your Queue to your Bookshelf.")
        else:
            return jsonify("This book is already on your Bookshelf")
    else:
        return jsonify("Oops...something went wrong.")


# add books to the browsed db
@bookDB.route('/add_browse', methods=['POST'])
def add_browse():
    book = request.json
    title = book['result']['title']
    bool = list(db.browse.find({'title': title}))
    if len(bool) == 0:
        db.browse.insert_one(book)
        return jsonify("")
    else:
        return jsonify("")


# display books in the browsed db
@bookDB.route('/display_browsed')
def display_browsed():
    displayBrowsed = db.browse.find().sort('_id', -1).limit(14)
    dataJSON = []
    for data in displayBrowsed:
        image = data['result']['image']
        title = data['result']['title']
        author = data['result']['author']
        dataDict = {
            'image': image,
            'title': title,
            'author': author
        }
        dataJSON.append(dataDict)
    return dataJSON


# displays information about a single book
@bookDB.route('/display_info', methods=['POST', 'GET'])
def display_info():
    query = request.json
    displayInfo = list(db.queue.find({'result.title': query}))
    if len(displayInfo) == 0:
        displayInfo = list(db.books.find({'result.title': query}))
        if len(displayInfo) == 0:
            displayInfo = list(db.browse.find({'result.title': query}))
            if len(displayInfo) == 0:
                return jsonify("Oops...something went wrong!")
    for data in displayInfo:
        image = data['result']['image']
        title = data['result']['title']
        author = data['result']['author']
        description = data['result']['description']
        category = data['result']['category']
        pageCount = data['result']['pageCount']
        publishedDate = data['result']['publishedDate']
        publisher = data['result']['publisher']
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
    return dataDict


# add a book to favorites
@bookDB.route('/add_fav', methods=['POST'])
def add_fav():
    book = request.json
    print(book)
    title = book['result']['title']
    inFavorite = list(db.favorites.find({'result.title': title}))
    if len(inFavorite) == 0:
        bool = list(db.favorites.find({'result.title': title}))
        if len(bool) == 0:
            db.favorites.insert_one(book)
            return jsonify("This book has been added to your Favorites.")
    else:
        return jsonify("This book is already in your Favorites.")


# display books in favorites
@bookDB.route('/display_favorites')
def display_favorites():
    displayFavorites = db.favorites.find().sort('result.title', 1)
    dataJSON = []
    for data in displayFavorites:
        image = data['result']['image']
        title = data['result']['title']
        author = data['result']['author']
        dataDict = {
            'image': image,
            'title': title,
            'author': author
        }
        dataJSON.append(dataDict)
    return dataJSON
