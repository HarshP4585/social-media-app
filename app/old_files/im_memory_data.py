import json
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Schema
# - get all the values from the body
# - data validation
# - force the (client/frontend) to send data in a schema that we expect
# - using "pydantic" -> define schema (can be used with any python code, independent from fastAPI)

# class Dummy(BaseModel): # Dummy Model
#     # title: string
#     # content: string
    
#     title: str
#     content: str
#     published: bool = True # optional field, default value
#     rating: Optional[int] = None # optional field, default to None

# @app.get("/get_data")
# def get_data():
#     return {"key": "value"}

# @app.post("/post_data")
# # def post_data(payload: dict = Body(...)):
# def post_data(dummy_post_payload: Dummy):
#     # pydantic model -> dict
#     return {"created": dummy_post_payload.dict()}


# CRUD
# Create -> POST /posts
# Read  -> GET /posts
#       -> GET /posts/:id
# Update -> PUT(all field to be sent)/PATCH(only field to be updated to be sent) /posts/:id
# Delete -> DELETE /posts/:id

id_counter = 3
my_posts = [
    {
        "id": 1,
        "title": "My First Post",
        "content": "Excited..."
    },
    {
        "id": 2,
        "title": "Trip to Dubai",
        "content": "Thrilled!"
    }
]

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    ratings: Optional[int] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.get("/posts/{id}")
# by default every path variables will be string but, we can add validations by providing the expected type
def get_post(id: int, response: Response):
    post = find_post(id)
    if post:
        return {"data": post}

    # response.status_code = status.HTTP_404_NOT_FOUND
    # return {"data": "post not found"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="post not found"
    )

@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED # set default status code
)
def save_post(payload: Post):
    global id_counter
    payload_dict = payload.dict()
    payload_dict["id"] = id_counter
    id_counter += 1
    my_posts.append(payload_dict)
    return {"created": payload_dict}

@app.patch("/posts/{id}")
def update_post(id: int, payload: PostUpdate):
    post = find_post(id)
    payload_dict = payload.dict()
    if post:
        for attr in post:
            if attr in payload_dict and payload_dict[attr]:
                post[attr] = payload_dict[attr]
        return Response(
            status_code=status.HTTP_200_OK,
            content=json.dumps({"data": f"post with id: {id} updated"}),
            media_type="application/json"
        )
    return Response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json.dumps({"data": f"post with id: {id} not found"}),
        media_type="application/json"
    )

@app.delete("/posts/{id}")
def delete_post(id: int):
    post = find_post(id)
    if post:
        my_posts.remove(post)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(
        status_code=status.HTTP_404_NOT_FOUND,
        content=json.dumps({"data": f"no post found with id: {id}"}),
        media_type="application/json"
    )
