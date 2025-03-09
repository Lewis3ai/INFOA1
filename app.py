import csv
import os
from flask import Flask, jsonify
from models import db, Pokemon, User, UserPokemon

app = Flask(__name__)

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pokemon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
                # Handle the case where height_m might be empty
                height_value = None
                if row["height_m"] and row["height_m"].strip():
                    try:
                        height_value = float(row["height_m"])
                    except ValueError:
                        height_value = None

                pokemon = Pokemon(
                    id=int(row["pokedex_number"]),
                    name=row["name"],
                    attack=int(row["attack"]),
                    defense=int(row["defense"]),
                    hp=int(row["hp"]),
                    height=height_value,
                    sp_attack=int(row["sp_attack"]),
                    sp_defense=int(row["sp_defense"]),
                    speed=int(row["speed"]),
                    type1=row["type1"],
                    type2=row["type2"] if row["type2"] and row["type2"] != "0" else None
                )
                db.session.add(pokemon)

        db.session.commit()

@app.route('/init', methods=['GET'])
def init():
    """Route to initialize the database."""
    initialize_db()
    return jsonify({"message": "Database initialized successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)