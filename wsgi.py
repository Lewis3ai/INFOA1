import click
import csv
from tabulate import tabulate
from App import db, User, Pokemon, UserPokemon
from App import app

@app.cli.command("init", help="Creates and initializes the database")
def initialize_db():
    with app.app_context():
        db.create_all()
    print("Database Initialized!")