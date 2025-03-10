import click
import csv
from tabulate import tabulate
from models import db, User, Pokemon, UserPokemon
from app import app




@app.cli.command("init", help="Creates and initializes the database")
def initialize_db(app):
  db.init_app(app)
  print("Database Initialized!")