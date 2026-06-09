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
    allow_headers=['*'],
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
            {'role': 'user',   'content': user_prompt}
        ]
    )

    generated_text = completion.choices[0].message.content
    tokens_used = (
        completion.usage.prompt_tokens +
        completion.usage.completion_tokens
    )

    return {'prd': generated_text, 'tokens_used': tokens_used}


@app.post('/user-stories')
def user_stories(request: ProductRequest):

    system_prompt = (
        'You are a senior product manager. '
        'Generate user stories in the standard format: '
        'As a [user type], I want to [action], so that [benefit]. '
        'Generate exactly 8 user stories covering different user types. '
        'Number each story. Be specific to the product described.'
    )
    user_prompt = (
        f'Generate 8 user stories for: '
        f'Product: {request.product_name} '
        f'Description: {request.product_description}'
    )

    chat_completion = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        temperature=0.4,
        max_tokens=1024,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user',   'content': user_prompt}
        ]
    )

    return {
        'product_name': request.product_name,
        'user_stories': chat_completion.choices[0].message.content,
        'tokens_used': chat_completion.usage.total_tokens
    }


@app.post('/prioritize')
def prioritize(request: ProductRequest):

    system_prompt = (
        'You are a senior product manager. '
        'Analyze the product and create a MoSCoW prioritization list. '
        'MoSCoW stands for: Must Have, Should Have, Could Have, Won\'t Have. '
        'For each category list 3-4 specific features. '
        'Explain briefly WHY each feature is in that category. '
        'Format clearly with headers for each category.'
    )
    user_prompt = (
        f'Create a MoSCoW prioritization for: '
        f'Product: {request.product_name} '
        f'Description: {request.product_description}'
    )

    chat_completion = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        temperature=0.3,
        max_tokens=1024,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user',   'content': user_prompt}
        ]
    )

    return {
        'product_name': request.product_name,
        'prioritization': chat_completion.choices[0].message.content,
        'tokens_used': chat_completion.usage.total_tokens
    }