"""
Web Frontend for Knowledge RAG
Flask-based web interface for the Wikipedia RAG system.
"""

from flask import Flask, render_template, request, jsonify, stream_with_context, Response
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import wikipediaapi
import requests
import time
import json
from typing import List, Dict

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN")
)

# Configuration
CACHE_DIR = os.environ.get("CACHE_DIR", "./cache")

# Initialize Wikipedia API
wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='KnowledgeRAG/1.0 (https://github.com/skepee-PROTOTYPE/knowledge-rag)'
)


def get_persistent_client():
    """Initialize persistent ChromaDB client."""
    Path(CACHE_DIR).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CACHE_DIR)


def get_embedding(text: str) -> List[float]:
    """Get embedding vector for text."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    time.sleep(0.1)
    return response.data[0].embedding


def get_embeddings_batch(texts: List[str], batch_size: int = 20) -> List[List[float]]:
    """Get embeddings for multiple texts in batches."""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
            
            if i + batch_size < len(texts):
                time.sleep(1)
                
        except Exception as e:
            for text in batch:
                try:
                    emb = get_embedding(text)
                    embeddings.append(emb)
                    time.sleep(0.5)
                except:
                    embeddings.append([0.0] * 1536)
    
    return embeddings


def clean_query(query: str) -> str:
    """Clean the query for Wikipedia search."""
    question_words = ['what', 'is', 'are', 'who', 'when', 'where', 'why', 'how', 'does', 'do', 'did', 'can', 'could', 'would', 'should']
    words = query.lower().split()
    cleaned_words = [w.strip('?.,!;:') for w in words if w.lower() not in question_words]
    return ' '.join(cleaned_words) if cleaned_words else query


def search_wikipedia(query: str, max_results: int = 3) -> List[str]:
    """Search Wikipedia for relevant articles."""
    cleaned_query = clean_query(query)
    
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": cleaned_query,
        "limit": max_results,
        "format": "json"
    }
    
    headers = {
        "User-Agent": "KnowledgeRAG/1.0 (educational project)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data[1] if len(data) > 1 else []
    except:
        return []


def get_wikipedia_content(title: str) -> Dict[str, str]:
    """Retrieve Wikipedia article content."""
    page = wiki.page(title)
    
    if not page.exists():
        return None
    
    return {
        "title": page.title,
        "url": page.fullurl,
        "summary": page.summary,
        "content": page.text
    }


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    
    return chunks


def index_wikipedia_article(collection, article: Dict[str, str]):
    """Index a Wikipedia article."""
    try:
        existing = collection.get(ids=[f"article_{article['title']}"])
        if existing['ids']:
            return
    except:
        pass
    
    chunks = chunk_text(article['content'])
    
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({
            "source": "wikipedia",
            "title": article["title"],
            "url": article["url"],
            "chunk_id": i
        })
        ids.append(f"{article['title']}_chunk_{i}")
    
    embeddings = get_embeddings_batch(documents, batch_size=20)
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )


def semantic_search(collection, question: str, top_k: int = 5) -> List[Dict]:
    """Search the knowledge base."""
    question_embedding = get_embedding(question)
    
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )
    
    retrieved_chunks = []
    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "title": results["metadatas"][0][i]["title"],
            "url": results["metadatas"][0][i]["url"],
        })
    
    return retrieved_chunks


def generate_answer(question: str, retrieved_chunks: List[Dict]) -> tuple:
    """Generate answer with LLM."""
    context_parts = []
    sources = {}
    
    for chunk in retrieved_chunks:
        title = chunk['title']
        if title not in sources:
            sources[title] = {
                'url': chunk['url'],
                'index': len(sources) + 1
            }
        
        source_idx = sources[title]['index']
        context_parts.append(f"[{source_idx}] {chunk['text']}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""Answer the question based on the Wikipedia content provided below.
Include citations using [numbers] that correspond to the sources.

Context from Wikipedia:
{context}

Question: {question}

Provide a comprehensive answer with citations."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant that answers questions based on Wikipedia content. Always cite your sources using [number] format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    
    answer = response.choices[0].message.content
    return answer, sources


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Handle question submission."""
    data = request.json
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    try:
        # Initialize ChromaDB
        chroma_client = get_persistent_client()
        collection = chroma_client.get_or_create_collection(
            name="wikipedia_knowledge",
            metadata={"description": "Wikipedia articles for RAG"}
        )
        
        # Search Wikipedia
        article_titles = search_wikipedia(question, max_results=3)
        
        if not article_titles:
            return jsonify({'error': 'No Wikipedia articles found'}), 404
        
        # Retrieve and index articles
        for title in article_titles:
            article = get_wikipedia_content(title)
            if article:
                index_wikipedia_article(collection, article)
        
        # Search for relevant chunks
        retrieved_chunks = semantic_search(collection, question, top_k=5)
        
        # Generate answer
        answer, sources = generate_answer(question, retrieved_chunks)
        
        # Format sources
        sources_list = [
            {
                'title': title,
                'url': info['url'],
                'index': info['index']
            }
            for title, info in sources.items()
        ]
        
        return jsonify({
            'answer': answer,
            'sources': sources_list,
            'articles_found': article_titles
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get cache statistics."""
    try:
        chroma_client = get_persistent_client()
        collection = chroma_client.get_or_create_collection(
            name="wikipedia_knowledge",
            metadata={"description": "Wikipedia articles for RAG"}
        )
        
        results = collection.get()
        
        # Count unique articles
        articles = set()
        for metadata in results['metadatas']:
            articles.add(metadata['title'])
        
        return jsonify({
            'total_chunks': collection.count(),
            'total_articles': len(articles)
        })
    except:
        return jsonify({
            'total_chunks': 0,
            'total_articles': 0
        })


if __name__ == '__main__':
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN not found in environment variables")
        print("Please set GITHUB_TOKEN in .env file")
    else:
        print("🚀 Starting Knowledge RAG Web Server...")
        print("📍 Access the app at: http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
