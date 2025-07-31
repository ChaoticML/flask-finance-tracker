import os
from flask import Flask

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    # Configure the app.
    # SECRET_KEY is needed for Flask to secure session data.
    # DATABASE is the path where the SQLite database file will be saved.
    app.config.from_mapping(
        SECRET_KEY='dev', # Change this to a random string in production!
        DATABASE=os.path.join(app.instance_path, 'finance.db'),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # The folder probably already exists.

    # Initialize the database with our application
    from . import db
    db.init_app(app)

    # The app context is a good place to initialize things.
    with app.app_context():
        # Import and register our routes from the routes.py file.
        from . import routes
        app.register_blueprint(routes.bp)

    return app
