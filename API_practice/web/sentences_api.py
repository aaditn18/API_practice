from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import os
import bcrypt

sentences_api = Flask(__name__) 
api = Api(sentences_api)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDb              # db init
users = db['Users']

class Register(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        
        # check if valid username, pwd 
        if users.find_one({"username":username}) is not None:
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
            "sentence" : "",
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

class Store(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        sentence = input_data["sentence"]
        
        # verify credentials match and token count

        if users.find_one({"username": username}) is None or not verifyPwd(username, pwd):
            return jsonify({
                "status: ":302,
                "message: ": "incorrect credentials"
            })
        tokens = countTokens(username)
        if tokens <= 0:
            return jsonify({
                "status: ":301,
                "message: ": "insufficient tokens"
            })
        

        # store and return status w msg

        users.update_one({
            "username" : username
        }, {"$set":{
            "sentence" : sentence,
            "tokens" : tokens - 1
        }})

        ret = {
            "Status": 200,
            "Message": "Sentence stored"
        }

        return jsonify(ret)


class Retrieve(Resource):
    # Post method is used, and not get as the user has to input some data
    def post(self): 
        # get and read the data
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        if users.find_one({"username": username}) is not None and verifyPwd(username, pwd):
            tokens = countTokens(username)
            if tokens < 1:
                return jsonify({
                    "Status" : 301,
                    "Msg" : "Tokens over"
                })
            users.update_one({
                    "username" : username
                }, {"$set":{
                    "tokens" : tokens - 1
                }})
            return jsonify({
                "Status":200,
                "Sentence" : users.find({"username": username})[0]["sentence"]
                })
        else:
             return jsonify({
                "Status":302,
                "Message" : "Account not found"
                }) 

        
api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Retrieve, "/get")

if __name__ == "__main__":
    sentences_api.run(host='0.0.0.0', port=5003)
