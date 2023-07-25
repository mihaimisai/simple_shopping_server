from flask import Flask, jsonify, request, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

dbPass = os.environ['dbPass']

uri = f"mongodb+srv://2busymihai:{dbPass}@cluster0.qvu7rjj.mongodb.net/test?retryWrites=true&w=majority"
# connect to the mongodb cluster and then collection
cluster = MongoClient(uri)
db = cluster['test']
collection = db['test1']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['secret']

#confirm a successful connection
try:
    cluster.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def is_valid_user(userOrMail, password):
    userToCheck = collection.find_one({"$or": [{"username": userOrMail}, {"email": userOrMail}]})
    if userToCheck and userToCheck['password']==password:
      print('OK')
      return True
    else:
      print('FALSE')
      return False


@app.route("/data", methods=['GET'])
def get_data():
    try:
      result = collection.find()
      data = []
      for document in result:
        document["_id"]=str(document["_id"])
        data.append(document)
      return jsonify(data)
    except Exception as error:
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
  except Exception as error:
    return jsonify({"error": str(error)})
    
  
@app.route("/delete/<item_id>", methods=['DELETE'])
def delete(item_id):
    try:
        item_id = ObjectId(item_id)
        result = collection.delete_one({"_id": item_id})
        if result.deleted_count == 0:
            print(f"Item with ID {item_id} not found.")
            return jsonify({"error": "Item not found."})
        print(f"Item with ID {item_id} deleted.")
        return jsonify({"message": "Item deleted."})
    except Exception as error:
        print(f"Error deleting item: {str(error)}")
        return jsonify({"error": str(error)})


@app.route('/register', methods=['POST'])
def register():
  try:
    data = request.get_json()
    user_data = data['user']
    newUser = {
      'username': user_data['username'],
      'email': user_data['email'],
      'password': user_data['password'],
      'items': []
    }
    result = collection.insert_one(newUser)
    inserted_id = str(result.inserted_id)
    newUser['_id'] = inserted_id
    print(f"{newUser['username']} added successfully.")
    return jsonify(newUser)
  except Exception as error:
    print(f"Error: {str(error)}")
    return jsonify({'error': str(error)})

@app.route('/login', methods=['POST'])
def login():
  try:
    data = request.get_json()
    user_data = data['user']
    userOrMail = user_data['userOrMail']
    password = user_data['password']
    if is_valid_user(userOrMail, password):
            # If user is valid, return a success message or anything you want
      return jsonify({'message': 'Login successful'})
    else:
            # If user is not valid, return an error message or anything you want
      return jsonify({'error': 'Invalid user or password'})
    return jsonify(user)
  except Exception as error:
    print(f'Error: {str(error)}')
    return jsonify({'error': str(error)})    

@app.route('/check_login_status', methods=['GET'])
def check_login_status():
  try:
    return jsonify(False)
  except Exception as error:
    print(f'Error: {str(error)}')
    return jsonify({'error': str(error)})
    
    


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)