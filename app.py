import csv
import os
from flask import Flask, jsonify
from models import db, Pokemon

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
                pokemon = Pokemon(
                    id=int(row["id"]),
                    name=row["name"],
                    attack=int(row["attack"]),
                    defense=int(row["defense"]),
                    hp=int(row["hp"]),
                    height=int(row["height"]),
                    sp_attack=int(row["sp_attack"]),
                    sp_defense=int(row["sp_defense"]),
                    speed=int(row["speed"]),
                    type1=row["type1"],
                    type2=row["type2"] if row["type2"] else None
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