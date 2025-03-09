from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    pokemon = db.relationship("UserPokemon", back_populates="trainer")

    def set_password(self, password):
        """Hashes and stores the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def catch_pokemon(self, pokemon_id, name):
        """Adds a Pokemon to the user's collection."""
        pokemon = UserPokemon(user_id=self.id, pokemon_id=pokemon_id, name=name)
        db.session.add(pokemon)
        db.session.commit()

    def release_pokemon(self, pokemon_id, name):
        """Removes a Pokemon from the user's collection."""
        pokemon = UserPokemon.query.filter_by(user_id=self.id, pokemon_id=pokemon_id, name=name).first()
        if pokemon:
            db.session.delete(pokemon)
            db.session.commit()

    def rename_pokemon(self, pokemon_id, name):
        """Renames a captured Pokemon."""
        pokemon = UserPokemon.query.filter_by(user_id=self.id, pokemon_id=pokemon_id).first()
        if pokemon:
            pokemon.name = name
            db.session.commit()


# Pokemon Model
class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    hp = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    sp_attack = db.Column(db.Integer, nullable=False)
    sp_defense = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Integer, nullable=False)
    type1 = db.Column(db.String(20), nullable=False)
    type2 = db.Column(db.String(20), nullable=True)

    trainer = db.relationship("UserPokemon", back_populates="pokemon")

    def get_json(self):
        """Returns the Pokemon details as a JSON dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "attack": self.attack,
            "defense": self.defense,
            "hp": self.hp,
            "height": self.height,
            "sp_attack": self.sp_attack,
            "sp_defense": self.sp_defense,
            "speed": self.speed,
            "type1": self.type1,
            "type2": self.type2
        }


# UserPokemon Model (Many-to-Many Relationship)
class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey("pokemon.id"), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # Allows custom naming of Pokémon

    trainer = db.relationship("User", back_populates="pokemon")
    pokemon = db.relationship("Pokemon", back_populates="trainer")

    def get_json(self):
        """Returns user-owned Pokemon details as a JSON dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "pokemon_id": self.pokemon_id,
            "name": self.name
        }