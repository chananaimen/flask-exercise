from typing import Tuple
import json
from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)


# TODO: Implement the rest of the API here!

# @app.route("/users")
# def getuser():
#     return  db.get("users")
   
@app.route("/users/<id>")
def getuserbyid(id):
    data=db.getById("users",int(id))
    if data is None:
       return create_response({},404,"THE USER ISNT FOUND")
    else:
       return  create_response({'user':data})
    
@app.route("/users")
def getuserbyteam():
     data = db.get('users')
     team = request.args.get('team')
     if team == None:
        return create_response({"users":data}) 
     list=[]
     for item in data:
        if item["team"]==team:
           list.append(db.getById("users",int(item["id"])))
     return create_response({'users':list})


    
@app.route('/users', methods=['POST'])
def createuser():
    user=request.get_json()
    rfiled=["name","age","team"]
    if not all(filed in user for filed in rfiled):
        return create_response( {"None":None} , 422 ,"Missing data The object should contain: ID, name and team" )
    data=db.create("users",user)
    write_json()
    return create_response({'users':data},201)

@app.route('/users/<id>', methods=['PUT'])
def updateuser(id):
    user=request.get_json()
    data=db.updateById("users",int(id),user)
    if data==None:
     return create_response({"users":user} ,404 ,"id isnt exits" )   
    write_json()
    return create_response({'users':data},201)

@app.route('/users/<id>', methods=['DELETE'])
def removeuser(id):
   data = db.getById("users",int(id))
   if data == None:
         return create_response({} , 404 , "id isnt exits" )
   db.deleteById("users",int(id))     
   write_json()
   return create_response({},200,"")

def write_json():
     newdata=json.dumps({"users":db.get("users")})
     with open("mockdb/dummy_data.py",'w') as f: 
        f.write("initial_db_state="+newdata)
     
"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(debug=True)
