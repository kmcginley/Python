# create the application object as an instance of class Flask imported from the flask package
from flask import Flask
from config import Config

# Flask uses the location of the module defined by __name__ as a starting point when it loads resources
#such as template files
# app variable is defined as an instance of the class Flask in the __init__.py script
flaskInst = Flask(__name__)
flaskInst.config.from_object(Config)

# app package is defined by the app directory and the __init__.py script
from app import routes

