from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.Bank
users = db['users']
users.insert_one({
    "username":"bank",
    "balance":10000,
    "debt":0

})


def userExists(username):
    return users.find_one({"username":username}) is not None

def correctPwd(username, pwd):
    if users.find_one({"username":username}) is not None:
        hashed_pwd = users.find({"username":username})[0]["pwd"]
        return bcrypt.hashpw(pwd.encode('utf8'), hashed_pwd) == hashed_pwd
    return False

def returnCode(stat, optional):
    if stat == 200 and optional is not None:
        return jsonify({
            "status":200,
            "msg": "Success!",
            "debt": optional
        })
    elif stat == 200:
        return jsonify({
            "status":200,
            "msg": "Success!"
        })
    elif stat == 301:
        return jsonify({
            "status":301,
            "error": "invalid username"
        })
    elif stat == 302:
        return jsonify({
            "status":302,
            "error": "invalid pwd"
        })        
    elif stat == 303:
        return jsonify({
            "status":stat,
            "error": "insufficient balance"
        })
    elif stat == 304:
        return jsonify({
            "status":stat,
            "error": "negative amount invalid"
        })
    else:
        return jsonify({
            "status":305,
            "error": "invalid input field(s)"
        })

class Register(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]

        if userExists(username):
            return returnCode(301, None)

        users.insert_one({"username":username, 
                          "pwd": bcrypt.hashpw(pwd.encode('utf8'), bcrypt.gensalt()),
                          "balance":0,
                          "debt":0})
        return returnCode(200, None)

class Add(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        money = input_data["amount"]
        if not userExists(username):
            return returnCode(301, None)
        if not correctPwd(username, pwd):
            return returnCode(302, None)
        if money < 0:
            return returnCode(304, None)
        balance = users.find_one({"username":username})["balance"]
        users.update_one({"username":username},{
            "$set": {
                "balance": balance + money
            }
        })
        return returnCode(200, None)

class Withdraw(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        money = input_data["amount"]
        balance = users.find_one({"username":username})["balance"]
        if not userExists(username):
            return returnCode(301, None)
        if not correctPwd(username, pwd):
            return returnCode(302, None)
        if money>balance:
            return returnCode(303, None)
        if money < 0:
            return returnCode(304, None)
        users.update_one({"username":username},{
            "$set": {
                "balance": balance - money
            }
        })
        return returnCode(200, None)       
        

class Transfer(Resource):
    def post(self):
        input_data = request.get_json()
        username1 = input_data["username1"]
        username2 = input_data["username2"]
        pwd = input_data["pwd"]
        money = input_data["amount"]
        if not userExists(username1) or not userExists(username2):
            return returnCode(301, None)
        if not correctPwd(username1, pwd):
            return returnCode(302, None)
        balance1 = users.find_one({"username":username1})["balance"]
        balance2 = users.find_one({"username":username2})["balance"]
        if money>balance1:
            return returnCode(303, None)
        if money < 0:
            return returnCode(304, None)
        users.update_one({"username":username1},{
            "$set": {
                "balance": balance1 - money
            }
        })
        users.update_one({"username":username2},{
            "$set": {
                "balance": balance2 + money
            }
        })        
        return returnCode(200, None)       

class CheckBalance(Resource):
    def post(self):
        input_data = request.get_json()
        username = input_data["username"]
        pwd = input_data["pwd"]
        if not userExists(username):
            return returnCode(301, None)
        if not correctPwd(username, pwd):
            return returnCode(302, None)
        balance = users.find_one({"username":username})["balance"]
        return jsonify({
            "status" : 200,
            "balance" : balance,
            "debt": users.find_one({"username":username})["debt"]
        })

class TakeLoan(Resource):
    def post(self):
        input_data = request.get_json()
        username1 = input_data["username"]
        username2 = "bank"
        pwd = input_data["pwd"]
        money = input_data["amount"]
        if not userExists(username1) or not userExists(username2):
            return returnCode(301, None)
        if not correctPwd(username1, pwd):
            return returnCode(302, None)
        balance1 = users.find_one({"username":username1})["balance"]
        debt = users.find_one({"username":username1})["debt"]
        balance2 = users.find_one({"username":username2})["balance"]
        if money < 0:
            return returnCode(304, None)
        users.update_one({"username":username1},{
            "$set": {
                "balance": balance1 + money,
                "debt": debt + money
            }
        })
        users.update_one({"username":username2},{
            "$set": {
                "balance": balance2 - money
            }
        })        
        return returnCode(200, debt+money)  

class PayLoan(Resource):
    def post(self):
        input_data = request.get_json()
        username1 = input_data["username"]
        username2 = "bank"
        pwd = input_data["pwd"]
        money = input_data["amount"]
        if not userExists(username1) or not userExists(username2):
            return returnCode(301, None)
        if not correctPwd(username1, pwd):
            return returnCode(302, None)
        balance1 = users.find_one({"username":username1})["balance"]
        debt = users.find_one({"username":username1})["debt"]
        balance2 = users.find_one({"username":username2})["balance"]
        if money > debt:
            return jsonify({
                "status": 305,
                "error": "you cannot pay more than your debt"
            })
        if money > balance1:
            return returnCode(303, None)
        if money < 0:
            return returnCode(304, None)
        users.update_one({"username":username1},{
            "$set": {
                "balance": balance1 - money,
                "debt": debt - money
            }
        })
        users.update_one({"username":username2},{
            "$set": {
                "balance": balance2 + money
            }
        })        
        return returnCode(200, debt-money) 

api.add_resource(Register, "/register")
api.add_resource(Add, "/add")
api.add_resource(Withdraw, "/take")
api.add_resource(Transfer, "/transfer")
api.add_resource(CheckBalance, "/balance")
api.add_resource(TakeLoan, "/takeloan")
api.add_resource(PayLoan, "/payloan")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port="5005")
