from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/catsdb")
mongo = PyMongo(app)
cats_collection = mongo.db.cats


@app.route('/')
def home():
    return "API is running!"


@app.route('/cats', methods=['POST'])
def create_cat():
    data = request.json
    if not all(field in data for field in ('name', 'description', 'birth_date')):
        return jsonify({"error": "Missing fields"}), 400

    cat = {
        "name": data["name"],
        "description": data["description"],
        "birth_date": data["birth_date"]
    }

    result = cats_collection.insert_one(cat)
    cat["_id"] = str(result.inserted_id)
    return jsonify(cat), 


@app.route('/cats', methods=['GET'])
def get_cats():
    cats = []
    for cat in cats_collection.find():
        cat["_id"] = str(cat["_id"])
        cats.append(cat)
    return jsonify(cats)


@app.route('/cats/<cat_id>', methods=['GET'])
def get_cat(cat_id):
    cat = cats_collection.find_one({"_id": ObjectId(cat_id)})
    if cat:
        cat["_id"] = str(cat["_id"])
        return jsonify(cat)
    return jsonify({"error": "Cat not found"}), 404


@app.route('/cats/<cat_id>', methods=['PUT'])
def update_cat(cat_id):
    data = request.json
    updated_data = {k: v for k, v in data.items() if k in ["name", "description", "birth_date"]}

    result = cats_collection.update_one({"_id": ObjectId(cat_id)}, {"$set": updated_data})
    if result.matched_count == 0:
        return jsonify({"error": "Cat not found"}), 404
    return jsonify({"message": "Cat updated successfully"})


@app.route('/cats/<cat_id>', methods=['DELETE'])
def delete_cat(cat_id):
    result = cats_collection.delete_one({"_id": ObjectId(cat_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Cat not found"}), 404
    return jsonify({"message": "Cat deleted successfully"})
if __name__ == '__main__':
    app.run(debug=True)

