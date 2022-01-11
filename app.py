from flask import Flask
from flask_cors import CORS

import testcontroller

app = Flask(__name__)

CORS(app)

app.register_blueprint(testcontroller.profile)


