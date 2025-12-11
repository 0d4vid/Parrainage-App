import os
import click
from flask import Flask, jsonify
from flask.cli import with_appcontext
from flask_cors import CORS

from .database import db
from . import routes # Import routes blueprint

# --- App Configuration ---
app = Flask(__name__)

# Set up CORS for all domains on all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Get the absolute path of the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Configure the database URI
# It will look for the db file in backend/data/parrainage.db
db_path = os.path.join(project_dir, 'data', 'parrainage.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# --- Routes ---
# Register the blueprint from routes.py
app.register_blueprint(routes.api_bp)

@app.route("/")
def index():
    """A simple route to check if the server is running."""
    return jsonify({"status": "Server is running"}), 200

# --- CLI Commands ---
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    # Ensure the data directory exists
    data_dir = os.path.join(project_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Check if db file exists and delete it to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)
        
    from .models import Promotion
    
    db.create_all()
    
    # Populate promotions
    promotions_to_add = ['B1', 'B2', 'B3', 'M1', 'M2']
    for promo_code in promotions_to_add:
        if not Promotion.query.filter_by(code=promo_code).first():
            promo = Promotion(code=promo_code)
            db.session.add(promo)
    
    db.session.commit()
    click.echo('Initialized the database and populated promotions.')

# Add the command to the app
app.cli.add_command(init_db_command)

if __name__ == '__main__':
    # This allows running the app directly for development
    # In a production environment, a WSGI server like Gunicorn or Waitress would be used.
    app.run(debug=True)
