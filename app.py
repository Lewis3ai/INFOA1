import csv
from flask import Flask
from models import db, Pokemon

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def initialize_db():
    with app.app_context():
        db.create_all()

        # Read CSV and add Pokémon to the database
        with open("pokemon.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["name"]
                type1 = row["type1"]
                type2 = row["type2"] if row["type2"] else None  # Handle empty type2

                if not Pokemon.query.filter_by(name=name).first():  # Avoid duplicates
                    pokemon = Pokemon(name=name, type1=type1, type2=type2)
                    db.session.add(pokemon)

        db.session.commit()
        print("Database Initialized Successfully!")

@app.cli.command("init")
def init():
    initialize_db()