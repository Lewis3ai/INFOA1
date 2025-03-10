from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this in production

db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_pokemon = db.relationship('UserPokemon', backref='owner', lazy=True)

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == '__main__':
     app.run(host='0.0.0.0', port=8080, debug=True)