from flask import Flask, jsonify, request
from pymongo import MongoClient
import os

dbPass = os.environ['dbPass']
jwtKey = os.environ['jwtKey']

uri = f"mongodb+srv://2busymihai:{dbPass}@cluster0.qvu7rjj.mongodb.net/test?retryWrites=true&w=majority"
# Create a new client and connect to the server
cluster = MongoClient(uri)
db = cluster['test']
collection = db['test1']

app = Flask(__name__)

# Send a ping to confirm a successful connection
try:
    cluster.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route("/data", methods=['GET'])
def get_data():
    try:
      from bson.objectid import ObjectId
      result = collection.find()
      data = []
      for document in result:
        document["_id"]=str(document["_id"])
        data.append(document)
      return jsonify(data)
    except error:
      return jsonify({"error": str(error)})
      

@app.route("/add_data", methods=['POST'])
def add_data():
  try:
    data = request.get_json()
    newItem = {'name': data['name']}
    result = collection.insert_one(newItem)
    inserted_id = str(result.inserted_id)
    newItem['_id'] = inserted_id
    return jsonify(newItem)
  except error:
    return jsonify({"error": str(error)})
    
  
@app.route("/delete/<item_id>", methods=['DELETE'])
def delete(item_id):
    try:
        from bson.objectid import ObjectId
        item_id = ObjectId(item_id)
        result = collection.delete_one({"_id": item_id})
        if result.deleted_count == 0:
            print(f"Item with ID {item_id} not found.")
            return jsonify({"error": "Item not found."}), 404
        print(f"Item with ID {item_id} deleted successfully.")
        return jsonify({"message": "Item deleted successfully."}), 200
    except error:
        print(f"Error deleting item: {str(error)}")
        return jsonify({"error": str(error)})



if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)