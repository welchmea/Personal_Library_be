from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from blueprints.main.views import main
from blueprints.price.views import bookprice
from blueprints.database.views import bookDB

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(main)
app.register_blueprint(bookprice)
app.register_blueprint(bookDB)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
