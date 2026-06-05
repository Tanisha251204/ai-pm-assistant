from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello! My AI PM Assistant is alive!"}


@app.get("/about")
def about():
    return {
        "project": "AI PM Assistant",
        "version": "1.0",
        "description": "Generates PRDs, user stories and feature plans using AI"
    }


class ProductRequest(BaseModel):
    product_name: str
    product_description: str


@app.post("/generate")
def generate(request: ProductRequest):
    return {
        "product_name": request.product_name,
        "message": f"You want to generate a PRD for: {request.product_name}",
        "description_received": request.product_description,
        "status": "AI generation coming in Week 2!"
    }