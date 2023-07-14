from flask import Flask, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection setup
uri = "mongodb+srv://2busymihai:testingdb@cluster0.qvu7rjj.mongodb.net/test?retryWrites=true&w=majority"
cluster = MongoClient(uri)
db = cluster['test']
collection = db['test1']

# API endpoint for retrieving data
@app.route('/', methods=['GET'])
def get_data():
    result = list(collection.find())  # Convert the cursor object to a list

    return jsonify(result)  # Convert the result to JSON format and return it

if __name__ == '__main__':
    app.run()
