from flask import Flask, jsonify, request
# jsonify is to convert dictionary into json format for return message body
# request is used so we can parse the message body that was sent in a post request for ex.

app = Flask(__name__) # flask app's name, this is the constructor
# __name__ is just a convention

# '/' is the keyword which makes flask understand there is 
# a request and the method needs to run
#request must end w/ one of the routes specified
# if route ending found, 200 ok will be status code for response
# if ending not found, 404 file not found error will be status code
# response to get/post request will be status followed by message body (possibly json)
# The three routes below are all for get requests, no message body, so they're not post reqs
@app.route('/')  
# by default methods param of route= ['GET']
def hello_world():
    # currently this method can only handle get requests, not post requests
    return "Hello World!"

@app.route('/bye')
def bye():
    # prepare response for request ending with /bye
    # do any computations if needed
    # return types: str, json, page

    # usually webservices and apis return json 
    # response after paarsing a json request

    # webapps return pages
    
    return "/bye requested, so now gonna exit"

@app.route("/add_2_nums", methods = ["POST"])
def add_nums():
    # not in json format, in dict form
    input_data = request.get_json() 
    if "x" not in input_data or "y" not in input_data:
        # 305 is status code sent explicitly
        return "WRONG", 305
    
    return jsonify({
        "z": input_data["x"] + input_data["y"]
    })



'''Server/browser communications are done through text
   including an image/video,
   Json is a format of text which is easy to use
   nested jsons and arrays can also exist'''
@app.route('/give json')
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
    app.run(debug = True)
    # debug = True as parameter during 
    # development to understand error
    # specify host and port during deployment