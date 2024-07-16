from flask import Flask, jsonify, request
from flask_restful import Api, Resource

arithemtic_restful_api = Flask(__name__) 
api = Api(arithemtic_restful_api)


# Define classes of Resource for each method
# within resource method chart
# Then define functionalities for diff request types
class Add(Resource):
    def post(self):
        input = request.get_json()
        try:
            return jsonify({
                "message":int(input['x']) + int(input['y']),
                "status":200
            })
        except:
            return jsonify({
                "message":"ERROR",
                "status":301
            })



class Subtract(Resource):
    def post(self):
        input = request.get_json()
        try:
            return jsonify({
                "message":int(input['x']) - int(input['y']),
                "status":200
            })
        except:
            return jsonify({
                "message":"ERROR",
                "status":301
            })

class Multiply(Resource):
    def post(self):
        input = request.get_json()
        try:
            return jsonify({
                "message":int(input['x']) * int(input['y']),
                "status":200
            })
        except:
            return jsonify({
                "message":"ERROR",
                "status":301
            })

class Divide(Resource):
    def post(self):
        input = request.get_json()
        try:
            if input["y"] == 0:
                return jsonify({
                "message": "Div by zero error",
                "status": 302
            })
            
            return jsonify({
                "message":(int(input['x'])*1.0) / int(input['y']),
                "status":200
            })
        except:
            return jsonify({
                "message":"ERROR",
                "status":301
            })


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/division")

@arithemtic_restful_api.route('/')  
def hello_world():
    return "Hello World!"

@arithemtic_restful_api.route('/bye')
def bye():
    return "/bye requested, so now gonna exit"

@arithemtic_restful_api.route("/add_2_nums", methods = ["POST"])
def add_nums():
    input_data = request.get_json() 
    if "x" not in input_data or "y" not in input_data:
        return "WRONG", 305
    
    return jsonify({
        "z": input_data["x"] + input_data["y"]
    })



@arithemtic_restful_api.route('/give json')
def give_json():
    ret = {
        "user" : "aadit",
        "file requested" : "json",
        "json keys are strings typically w/o fancy special symbols" : 4,
        "arr" : [1,2,3,4],
        "arr2" : ["hi", "bye", 5],
        "accounts" : [
            {
                    "username": "aku",
                    "pwd":123
            },
            {
                    "username": "aku18",
                    "pwd":1290
            }
        ]
                        
        
    }
    return jsonify(ret)



if __name__ == "__main__":
    arithemtic_restful_api.run(debug = True)