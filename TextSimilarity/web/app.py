from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import os
import bcrypt
import spacy

app = Flask(__name__) 
api = Api(app)

# Access your Flask application using the new port in your browser or API client:
# Copy
# http://localhost:5001


client = MongoClient("mongodb://db:27017")
db = client.SimilarTextDB             # db init
users = db['Users']

class Register(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        
        # check if username already exists, pwd is proper or not
        if users.find_one({"username":username}) is not None:
            # Use .count() == 0 to check using .find()
            return jsonify({
            "Status": 301,
            "Message": "Username already in use"
        })
        if len(pwd) < 8:
            return jsonify({
            "Status": 302,
            "Message": "Pwd too short"
        })
        hashed_pw = bcrypt.hashpw(pwd.encode('utf8'), bcrypt.gensalt())
        users.insert_one({
            "username" : username,
            "pwd" : hashed_pw,
            "tokens" : 6

        })

        ret = {
            "Status": 200,
            "Message": "Successful API Registration"
        }

        return jsonify(ret)
    
def verifyPwd(username, pwd):
    hashed_pwd = users.find({"username":username})[0]["pwd"]
    return bcrypt.hashpw(pwd.encode('utf8'), hashed_pwd) == hashed_pwd

def countTokens(username):
    return users.find({"username": username})[0]["tokens"]
    

class Detect(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        if users.find_one({"username": username}) is None or not verifyPwd(username, pwd):
            return jsonify({
                "status: ":302,
                "message: ": "incorrect username/pwd"
            })
        tokens = countTokens(username)
        if tokens <= 0:
            return jsonify({
                "status: ":301,
                "message: ": "Insufficient tokens, please refill!"
            })
        
        text1 = input_data['text1']
        text2 = input_data['text2']

        # Calculate edit distance
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2)
        users.update_one({'username':username}, {
            "$set":{"tokens": tokens-1}
        })

        return jsonify({
            "Status " : 200,
            "Similarity " : f"{ratio*100}%",
            "Tokens Remaining": tokens-1
        })
    
class Refill(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        auth_pwd =  input_data["auth_pwd"]
        if users.find_one({"username": username}) is None:
            return jsonify({
                "status: ":302,
                "message: ": "incorrect username"
            })

        # check auth, hardcoded for now, not irw projects
        correct_pwd = "13dbjhq182rhc"
        if auth_pwd != correct_pwd:
            return jsonify({
                "status: ":303,
                "message: ": "incorrect admin pwd"
            })            


        tokens = countTokens(username)
        newTokens = input_data["new_tokens"]   
        users.update_one({'username':username}, {
            "$set":{"tokens": tokens + newTokens}
        })

        return jsonify({
            "Status " : 200,
            "Message": "Refill successful"
        })        
api.add_resource(Register, "/register")
api.add_resource(Detect, "/Detect")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)