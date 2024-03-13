from flask import Flask, jsonify, request, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from flask_cors import CORS

dbPass = os.environ['dbPass']

uri = f"mongodb+srv://2busymihai:{dbPass}@cluster0.qvu7rjj.mongodb.net/test?retryWrites=true&w=majority"
# connect to the mongodb cluster and then collection
cluster = MongoClient(uri)
db = cluster['test']
collection = db['test1']

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ['secret']

#confirm a successful connection
try:
  cluster.admin.command('ping')
  print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
  print(e)


def is_valid_user(userOrMail, password):
  userToCheck = collection.find_one(
    {"$or": [{
      "username": userOrMail
    }, {
      "email": userOrMail
    }]})
  if userToCheck and userToCheck['password'] == password:
    return True
  else:
    return False


@app.route("/data", methods=['GET'])
def data():
  try:
    user_id = session.get('user_id')
    if not user_id:
      return jsonify({"error": "User not logged in."})

    user_id = ObjectId(user_id)
    user = collection.find_one({"_id": user_id})
    items = user['items']
    #print(items)
    itemsArray = []
    for item in items:
      itemsArray.append(item)
    return jsonify(itemsArray)
  except Exception as error:
    return jsonify({"error": str(error)})


@app.route("/add_data", methods=['POST'])
def add_data():
  try:
    #print("Add data route reached.")
    user_id = session.get('user_id')
    if not user_id:
      return jsonify({"error": "User not logged in."})

    data = request.get_json()
    #print("Received data:", data)
    new_item = data['itemName']
    #print("New item: ", new_item)
    # Find the user in the database
    user_id = ObjectId(user_id)
    user = collection.find_one({"_id": user_id})

    # Add the new item to the existing 'items' array and push it back into db
    new_items_list = user['items']
    new_items_list.append(new_item)
    collection.update_one({"_id": ObjectId(user_id)},
                          {'$set': {
                            "items": new_items_list
                          }})

    return jsonify(new_item)

  except Exception as error:
    return jsonify({"error": str(error)})


@app.route("/delete/", methods=['DELETE'])
def delete():
  try:
    #print("Delete data route reached")
    user_id = session.get('user_id')
    if not user_id:
      return jsonify({"error": "User not logged in."})

    data = request.get_json()
    item_to_delete = data.get('itemName')
    #print(item_to_delete)

    user_id = ObjectId(user_id)
    user = collection.find_one({"_id": user_id})
    new_item_list = user['items']
    #print(new_item_list)
    new_item_list.remove(item_to_delete)
    #print(new_item_list)

    collection.update_one({'_id': ObjectId(user_id)},
                          {'$set': {
                            'items': new_item_list
                          }})

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
    session['user_id'] = inserted_id
    #print(session['user_id'])
    #print(f"{newUser['username']} added successfully.")
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
      userToCheck = collection.find_one(
        {"$or": [{
          "username": userOrMail
        }, {
          "email": userOrMail
        }]})
      session['user_id'] = str(userToCheck['_id'])
      return jsonify({'message': 'Login successful'}), 200
    else:
      return jsonify({'error': 'Invalid user or password'}), 401
  except Exception as error:
    print(f'Error: {str(error)}')
    return jsonify({'error': str(error)}), 500


@app.route('/check_login_status', methods=['GET'])
def check_login_status():
  try:
    user_id = session.get('user_id')
    if user_id:
      # print(user_id)
      # User is logged in
      return jsonify(True)
    else:
      #print(user_id)
      # User is not logged in
      return jsonify(False)
  except Exception as error:
    return jsonify({"error": str(error)})


@app.route('/logout', methods=['POST'])
def logout():
  try:
    session.pop('user_id')
    return jsonify({"logged_in": False})
  except Exception as error:
    return jsonify({"error": str(error)})


@app.route('/api')
def flask_status():

  return jsonify('Flask is up')


if __name__ == "__main__":
  app.run("0.0.0.0", debug=True)
