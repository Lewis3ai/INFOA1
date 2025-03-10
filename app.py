import csv
import os
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Pokemon, User, UserPokemon

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)

db.init_app(app)

def initialize_db():
    """Parses pokemon.csv and stores Pokémon in the database."""
    with app.app_context():
        db.drop_all()  # Reset the database each time
        db.create_all()

        # Read CSV file
        csv_file_path = os.path.join(os.path.dirname(__file__), "pokemon.csv")
        with open(csv_file_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if "id" not in row or not row["id"].isdigit():
                    continue  # Skip invalid rows

                pokemon = Pokemon(
                    id=int(row["id"]),
                    name=row.get("name", "Unknown"),
                    attack=int(row.get("attack", 0)),
                    defense=int(row.get("defense", 0)),
                    hp=int(row.get("hp", 0)),
                    height=int(row.get("height", 0)),
                    sp_attack=int(row.get("sp_attack", 0)),
                    sp_defense=int(row.get("sp_defense", 0)),
                    speed=int(row.get("speed", 0)),
                    type1=row.get("type1", "Unknown"),
                    type2=row.get("type2") if row.get("type2") else None
                )
                db.session.add(pokemon)

        db.session.commit()

@app.route('/init', methods=['GET'])
def init():
    """Route to initialize the database."""
    initialize_db()
    return jsonify({"message": "Database initialized successfully"}), 200

@app.route('/register', methods=['POST'])
def register():
    """Registers a new user."""
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Logs in a user and returns a JWT token."""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=user.id)
    response = jsonify({"message": "Login successful", "token": access_token})
    response.set_cookie("access_token", access_token, httponly=True)

    return response, 200

@app.route('/catch', methods=['POST'])
@jwt_required()
def catch_pokemon():
    """Allows a user to catch a Pokemon."""
    user_id = get_jwt_identity()
    data = request.get_json()

    pokemon_id = data.get("pokemon_id")
    name = data.get("name")

    user = User.query.get(user_id)
    pokemon = Pokemon.query.get(pokemon_id)

    if not pokemon:
        return jsonify({"message": "Pokemon not found"}), 404

    user.catch_pokemon(pokemon_id, name)
    return jsonify({"message": "Pokemon caught successfully"}), 200

@app.route('/release', methods=['POST'])
@jwt_required()
def release_pokemon():
    """Allows a user to release a Pokemon."""
    user_id = get_jwt_identity()
    data = request.get_json()

    pokemon_id = data.get("pokemon_id")
    name = data.get("name")

    user = User.query.get(user_id)
    user.release_pokemon(pokemon_id, name)

    return jsonify({"message": "Pokemon released successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)