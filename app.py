import uuid
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

client = MongoClient(
    "mongodb+srv://koushik:rollsroy4u@traversycluster.ircunfq.mongodb.net/")
db = client["todos"]
collection = db["todo"]

app = FastAPI()


def generate_random_id():
    return str(uuid.uuid4())


class Item(BaseModel):
    id: str = generate_random_id()
    title: str
    description: str

    class Config:
        exclude = ("_id")


class Update_todo(BaseModel):
    title: str
    description: str


@app.get("/todos")
async def get_todos():
    todos = []
    all_todos = collection.find({}, {"_id": 0})
    for todo in all_todos:
        todos.append(Item(**todo))
    return todos


@app.post("/todos")
async def create_todo(item: Item):
    data = item.model_dump()
    create_todo = collection.insert_one(data)
    new_todo = collection.find_one(
        {"_id": create_todo.inserted_id}, {"_id": 0})
    if create_todo:
        return JSONResponse(content=new_todo)
    else:
        raise HTTPException(400, "Something went wrong")


@app.put("/todo/update/{todo_id}")
async def update_todo(todo_id: str, item: Update_todo):
    modify_todo = collection.update_one(
        {"id": todo_id}, {"$set": item.model_dump()})

    if modify_todo.modified_count == 0:
        raise HTTPException(400, "Something went wrong")

    updated_todo = collection.find_one(
        {"_id": todo_id}, {"_id": 0})

    if updated_todo is None:
        raise HTTPException(404, "Data is not found")
    else:
        return {"message": "Successfully updated todo"}


@app.delete("/todo/delete/{todo_id}")
async def delete_todo(todo_id: str):
    remove_todo = collection.delete_one({"id": todo_id})

    if remove_todo.deleted_count == 0:
        raise HTTPException(400, "Data not deleted SuccessFully")
    else:
        return {"message": "Successfully deleted todo"}
