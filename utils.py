import os
import hashlib

def generate_challenge():
    return os.urandom(16).hex()

def hash_response(password, challenge):
    combined = password + challenge
    return hashlib.sha256(combined.encode()).hexdigest()