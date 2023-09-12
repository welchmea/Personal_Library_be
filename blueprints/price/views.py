from flask import Blueprint, request
import requests

bookprice = Blueprint('price', __name__)


# web scrapes price from Barnes and Noble
@bookprice.route("/price")
def price():
    search = request.args.get('input')

    if not search:
        return "Enter a valid search!"

    # get request to partner's microservice
    param = {'name': search}

    url = 'https://book-price-microservice.up.railway.app/price'

    response = requests.get(url, params=param)

    return response.text
