import requests
from pymongo import MongoClient

# MongoDB connection details
MONGO_URI = "mongodb+srv://admin:admin@cluster0.ry4urfk.mongodb.net/"
DATABASE_NAME = "dp_1004"
COLLECTION_NAME = "pokemon"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# PokeAPI base URL
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def get_pokemon_data(pokemon_id):
    # Fetch data from PokeAPI
    response = requests.get(POKEAPI_BASE_URL + str(pokemon_id))
    if response.status_code == 200:
        pokemon_data = response.json()
        return {
            "id": pokemon_data["id"],
            "name": pokemon_data["name"],
            "base_experience": pokemon_data["base_experience"],
            "height": pokemon_data["height"],
            # Add more fields as needed
        }
    else:
        print(f"Failed to fetch data for Pokemon with ID {pokemon_id}")
        return None

# Insert data for ten Pokemon into MongoDB
for pokemon_id in range(1, 11):
    pokemon_data = get_pokemon_data(pokemon_id)
    if pokemon_data:
        # Insert into MongoDB
        result = collection.insert_one(pokemon_data)
        print(f"Pokemon with ID {pokemon_data['id']} inserted. Inserted ID: {result.inserted_id}")

# Close MongoDB connection
client.close()
