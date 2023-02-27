from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import db_helper
from data_extraction import *
import uuid
from recipe import Recipe, currently_opened_recipe
import pymongo
import pickle
import uvicorn
import os

url = os.environ.get("mongodb_url")
app = FastAPI()
app.mount("/assets", StaticFiles(directory="Template/assets"), name="assets")

templates = Jinja2Templates(directory="Template")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    unique_id = str(uuid.uuid4())
    return templates.TemplateResponse(
        "index.html", {"request": request, "unique_id": unique_id}
    )


class ChatbotInput(BaseModel):
    unique_id: str
    text: str


@app.post("/enter_text")
def send_text(data: ChatbotInput, request: Request):
    input_text = data.text.encode(encoding="ascii", errors="ignore").decode()
    unique_id = data.unique_id
    output_result = ""
    client = db_helper.client
    unique_id_find = client["RecipeEater"]["recipe_instances"].find_one(
        {"unique_id": unique_id}
    )
    if unique_id_find:
        recipe_object = pickle.loads(unique_id_find["recipe_object"])
        try:
            output_result = recipe_object.parse_text(input_text)
        except Exception as e:
            print(e)
        object_str = pickle.dumps(recipe_object)
        client["RecipeEater"]["recipe_instances"].update_one(
            {"unique_id": unique_id}, {"$set": {"recipe_object": object_str}}
        )
    else:
        recipe_object = Recipe(unique_id)
        output_result = recipe_object.parse_text(input_text)
        object_str = pickle.dumps(recipe_object)
        client["RecipeEater"]["recipe_instances"].insert_one(
            {"unique_id": unique_id, "recipe_object": object_str}
        )
    print(output_result)
    return output_result


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
