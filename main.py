import os
from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


class ProductRequest(BaseModel):
    product_name: str
    product_description: str


@app.get('/')
def home():
    return {'message': 'Hello! My AI PM Assistant is alive!'}


@app.get('/about')
def about():
    return {'project': 'AI PM Assistant', 'version': '2.0'}


@app.post('/generate')
def generate(request: ProductRequest):
    system_prompt = (
        'You are a senior PM. Write PRDs with: '
        '1.Problem Statement 2.Goals 3.User Personas '
        '4.Core Features 5.Out of Scope 6.Timeline'
    )
    user_prompt = (
        f'Generate PRD for: {request.product_name} '
        f'Description: {request.product_description}'
    )

    completion = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        max_tokens=8192,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )

    generated_text = completion.choices[0].message.content
    tokens_used = (
        completion.usage.prompt_tokens +
        completion.usage.completion_tokens
    )

    return {'prd': generated_text, 'tokens_used': tokens_used}