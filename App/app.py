import os, csv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    unset_jwt_cookies,
)
import click
from flask.cli import with_appcontext


from .models import db


# Configure Flask App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'MySecretKey'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_REFRESH_COOKIE_NAME'] = 'refresh_token'
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
# app.config['JWT_HEADER_TYPE'] = ""
app.config['JWT_HEADER_NAME'] = "Cookie"


# Initialize App 
db = SQLAlchemy(app)
db.init_app(app)
app.app_context().push()
CORS(app)
jwt = JWTManager(app)

@click.command("init-db")
@with_appcontext
def initialize_db():
    """Initialize the database."""
    db.drop_all()
    db.create_all()
    click.echo("Database initialized.")

app.cli.add_command(initialize_db)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_pokemon = db.relationship('UserPokemon', backref='owner', lazy=True)
    password_hash = db.Column(db.String(200), nullable=False)


class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(80), nullable=False)

class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)

@app.route('/mypokemon/', methods=['PUT'])
@jwt_required()
def update_pokemon():
    data = request.get_json()
    user_id = get_jwt_identity()
    user_pokemon = UserPokemon.query.filter_by(id=data.get('id'), user_id=user_id).first()

    if not user_pokemon:
        return jsonify({"error": f"Id {data.get('id')} is invalid or does not belong to {user_id}"}), 401

    user_pokemon.name = data.get('name', user_pokemon.name)
    db.session.commit()
    return jsonify({"message": f"{user_pokemon.name} updated successfully"})

@app.route('/mypokemon/', methods=['DELETE'])
@jwt_required()
def delete_pokemon():
    data = request.get_json()
    user_id = get_jwt_identity()
    user_pokemon = UserPokemon.query.filter_by(id=data.get('id'), user_id=user_id).first()

    if not user_pokemon:
        return jsonify({"error": f"Id {data.get('id')} is invalid or does not belong to {user_id}"}), 401

    db.session.delete(user_pokemon)
    db.session.commit()
    return jsonify({"message": f"{user_pokemon.name} released"})


@app.route('/')
def index():
    response_text = "<h1>Poke API v1.0</h1>"
    print(f"Returning response: {response_text}")  # Logs the response to the terminal
    return response_text




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
