import os
from groq import Groq
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import GeneratedDoc, create_tables, get_db
from pdf_generator import generate_pdf
from rag import add_document, retrieve_context, clear_documents

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

create_tables()


class ProductRequest(BaseModel):
    product_name: str
    product_description: str


@app.get('/')
def home():
    return {'message': 'Hello! My AI PM Assistant is alive!'}


@app.get('/about')
def about():
    return {
        'project': 'AI PM Assistant',
        'version': '3.0',
        'description': 'Generates PRDs using Groq + Llama 3 with history'
    }


@app.post('/upload')
async def upload_document(file: UploadFile = File(...)):

    content = await file.read()
    text = content.decode('utf-8', errors='ignore')

    if not text.strip():
        return {'error': 'File is empty or could not be read'}

    chunks_added = add_document(
        doc_id=file.filename,
        text=text,
        metadata={'filename': file.filename}
    )

    return {
        'message': 'Document uploaded successfully',
        'filename': file.filename,
        'chunks_stored': chunks_added
    }


@app.delete('/clear-documents')
def delete_documents():
    clear_documents()
    return {'message': 'All uploaded documents cleared'}


@app.post('/generate')
def generate(request: ProductRequest, db: Session = Depends(get_db)):

    # Retrieve relevant context from uploaded documents
    context = retrieve_context(
        f'{request.product_name} {request.product_description}'
    )

    # Build system prompt — include context if available
    if context:
        system_prompt = (
            'You are a senior PM. Write PRDs with: '
            '1.Problem Statement 2.Goals 3.Personas '
            '4.Features 5.Scope 6.Timeline. '
            'Use the following context from past documents '
            'to match the writing style and format:\n\n'
            + context
        )
    else:
        system_prompt = (
            'You are a senior PM. Write PRDs with: '
            '1.Problem Statement 2.Goals 3.Personas '
            '4.Features 5.Scope 6.Timeline'
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

    doc = GeneratedDoc(
        product_name=request.product_name,
        doc_type='prd',
        content=generated_text,
        tokens_used=tokens_used
    )
    db.add(doc)
    db.commit()

    return {
        'prd': generated_text,
        'tokens_used': tokens_used,
        'doc_id': doc.id
    }


@app.post('/user-stories')
def user_stories(request: ProductRequest, db: Session = Depends(get_db)):

    system_prompt = (
        'You are a senior PM. Generate 8 user stories: '
        'As a [user], I want to [action], so that [benefit].'
    )
    user_prompt = (
        f'Generate 8 user stories for: {request.product_name} '
        f'Description: {request.product_description}'
    )

    completion = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        temperature=0.4,
        max_tokens=1024,
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

    doc = GeneratedDoc(
        product_name=request.product_name,
        doc_type='user_stories',
        content=generated_text,
        tokens_used=tokens_used
    )
    db.add(doc)
    db.commit()

    return {
        'user_stories': generated_text,
        'tokens_used': tokens_used,
        'doc_id': doc.id
    }


@app.post('/prioritize')
def prioritize(request: ProductRequest, db: Session = Depends(get_db)):

    system_prompt = (
        'You are a senior PM. Create MoSCoW prioritization. '
        'Must Have, Should Have, Could Have, Wont Have. 3-4 features each.'
    )
    user_prompt = (
        f'MoSCoW for: {request.product_name} '
        f'Description: {request.product_description}'
    )

    completion = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        temperature=0.3,
        max_tokens=1024,
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

    doc = GeneratedDoc(
        product_name=request.product_name,
        doc_type='prioritization',
        content=generated_text,
        tokens_used=tokens_used
    )
    db.add(doc)
    db.commit()

    return {
        'prioritization': generated_text,
        'tokens_used': tokens_used,
        'doc_id': doc.id
    }


@app.get('/history')
def history(db: Session = Depends(get_db)):

    docs = db.query(GeneratedDoc).order_by(
        GeneratedDoc.created_at.desc()
    ).all()

    return {
        'total': len(docs),
        'history': [
            {
                'id':           doc.id,
                'product_name': doc.product_name,
                'doc_type':     doc.doc_type,
                'tokens_used':  doc.tokens_used,
                'created_at':   str(doc.created_at)
            }
            for doc in docs
        ]
    }


@app.get('/download/{doc_id}')
def download_pdf(doc_id: int, db: Session = Depends(get_db)):

    doc = db.query(GeneratedDoc).filter(
        GeneratedDoc.id == doc_id
    ).first()

    if not doc:
        return {'error': 'Document not found'}

    pdf_path = generate_pdf(
        product_name=doc.product_name,
        doc_type=doc.doc_type,
        content=doc.content
    )

    return FileResponse(
        path=pdf_path,
        media_type='application/pdf',
        filename=f'{doc.product_name}_{doc.doc_type}.pdf'
    )