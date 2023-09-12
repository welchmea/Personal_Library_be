from flask import Blueprint, request
import requests

main = Blueprint('main', __name__)


# typing in the search bar calls this route
@main.route("/")
def book():
    search = request.args.get('input')
    if not search:
        return "Enter a valid search!"

    maxResults = '15'
    # get request to Google Books API
    url = 'https://www.googleapis.com/books/v1/volumes'
    param = search
    querystring = {'q': param, 'maxResults': maxResults,
                   'orderBy': 'relevance', 'key': 'AIzaSyBkFXyRJFdICDMby_yDSHHZgdjH0MSTtLQ'}

    # query results
    response = requests.get(url, params=querystring)
    data = response.json()

    return data
