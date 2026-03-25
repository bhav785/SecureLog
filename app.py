from flask import Flask
from extensions import db, bcrypt
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)

CORS(app)

from auth import auth_routes
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)