from fastapi import FastAPI, HTTPException, Depends
import pyrebase
import uvicorn
from models import LoginSchema,SignUpSchema, Todo
from fastapi.responses import JSONResponse
from fastapi.requests import  Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app =  FastAPI(
        description="This is  a simple todo app",
        title="Todo App",
        docs_url="/"
    )


import firebase_admin
from firebase_admin import credentials, auth


if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)


firebaseConfig = {
  "apiKey": "AIzaSyDlNG-4_v__CNpl0nEbdwgG2MOS4ixp_2k",
  "authDomain": "todo-app-3110a.firebaseapp.com",
  "projectId": "todo-app-3110a",
  "storageBucket": "todo-app-3110a.appspot.com",
  "messagingSenderId": "707731811880",
  "appId": "1:707731811880:web:09021db143e4ce5ba90f1d",
  "measurementId": "G-HPBSYJDMYV",
  "databaseURL":"https://todo-app-3110a-default-rtdb.asia-southeast1.firebasedatabase.app/"
}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()




@app.post('/signup')
async def create_an_account(user_data:SignUpSchema):
    email = user_data.email
    password = user_data.password

    try:
        user = auth.create_user(email = email,password = password)
        return JSONResponse(content={
            "message": f"User Account Created for user {user.uid}",
        },   status_code=201)
    
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail=f"Account Already Created for {email} "
        )






@app.post('/login')
async def create_access_token(user_data:LoginSchema):
    email = user_data.email
    password = user_data.password

    try:
        user = firebase.auth().sign_in_with_email_and_password(email=email, password=password)

        token = user['idToken']
        return JSONResponse(content={
            "token":token
        }, status_code=200)
    except:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    


security = HTTPBearer()

def verify_token(auth_credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = auth_credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@app.post("/create_todo")
async def test(todo: Todo, user: dict = Depends(verify_token)):
    todo_dict = todo.model_dump()
    todo_dict['user_id'] = user['uid']
    doc_ref= db.child("todos").push(todo_dict)
    return doc_ref['name']

@app.get("/todos")
async def test(user: dict = Depends(verify_token)):
    try:
        todos= db.child("todos").order_by_child("user_id").equal_to(user["uid"]).get()
        user_todos = []
        if todos.each():
                user_todos = [{"id": todo.key(), **todo.val()} for todo in todos.each()]
        return JSONResponse(content={"user_todos": user_todos})
    except Exception as e:
        return {"error": str(e)}
    
@app.put("/update_todo/{id}")
async def update_todo(id: str, updated_todo: Todo, user: dict = Depends(verify_token)):
    try:
        existing_todo = db.child("todos").child(id).get().val()
        
        if not existing_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        if existing_todo.get("user_id") != user["uid"]:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        updated_todo_dict = updated_todo.dict()
        
        db.child("todos").child(id).update(updated_todo_dict)
        
        updated_item = db.child("todos").child(id).get().val()
        
        return {"msg": "Todo updated successfully", "updated_todo": updated_item}
        
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
    

@app.delete("/todos/{id}")
def delete_todo(id: str, user: dict = Depends(verify_token)):
    try:
        todo_item = db.child("todos").child(id).get().val()
        
        if not todo_item:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        if todo_item.get("user_id") != user["uid"]:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        db.child("todos").child(id).remove()
        return {"msg": "Deleted Successfully"}
        
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    uvicorn.run("main:app", reload=True)








