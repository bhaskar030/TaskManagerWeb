import os
from flask import Flask
from dotenv import load_dotenv
from routes.api import api as api_blueprint
from routes.pages import pages as pages_blueprint
from flask_cors import CORS
import logging
import gunicorn
import jwt

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Register blueprints
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(pages_blueprint)

CORS(app, origins=["http://localhost:3000"])  # Adjust as needed

@app.route('/')
def root():
    return "SEO Manager API is running"

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore")  # Ignore HTTPS warnings in dev
    logging.debug("Running in __main__")
    app.run(host='0.0.0.0', port=8000)
