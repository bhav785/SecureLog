from flask import Blueprint, request, jsonify
from models import db, User, Challenge
from extensions import db, bcrypt
from utils import generate_challenge, hash_response

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # check user exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    # hash password using bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(username=username, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})

@auth_routes.route('/login-challenge', methods=['POST'])
def login_challenge():
    data = request.json
    username = data.get('username')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    challenge = generate_challenge()

    # store challenge in DB
    challenge_entry = Challenge(username=username, challenge=challenge)
    db.session.add(challenge_entry)
    db.session.commit()

    return jsonify({
        "challenge": challenge,
        "message": "Challenge generated"
    })

@auth_routes.route('/login-verify', methods=['POST'])
def login_verify():
    data = request.json
    username = data.get('username')
    client_response = data.get('response')
    challenge_value = data.get('challenge')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # find challenge
    challenge_entry = Challenge.query.filter_by(
        username=username,
        challenge=challenge_value,
        used=False
    ).first()

    if not challenge_entry:
        return jsonify({"message": "Invalid or reused challenge (Replay Attack detected!)"}), 400

    # mark challenge as used (prevent replay)
    challenge_entry.used = True
    db.session.commit()

    # compute expected response
    # NOTE: we compare using stored hashed password (important!)
    expected_response = hash_response(user.password_hash, challenge_value)

    if expected_response != client_response:
        return jsonify({"message": "Authentication failed"}), 401

    return jsonify({"message": "Password verified. Proceed to OTP"})

