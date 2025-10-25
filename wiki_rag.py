"""
Wikipedia RAG System
Retrieves information from Wikipedia and uses RAG to answer questions with citations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
import wikipediaapi
import requests
import time
from typing import List, Dict

# Load environment variables
load_dotenv()

# Initialize OpenAI client for GitHub Models
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN")
)

# Configuration
CACHE_DIR = os.environ.get("CACHE_DIR", "./cache")
MAX_CACHE_SIZE = int(os.environ.get("MAX_CACHE_SIZE", 100))

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
    """Get embedding vector for text using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    # Add small delay to avoid rate limits
    time.sleep(0.1)
    return response.data[0].embedding


def get_embeddings_batch(texts: List[str], batch_size: int = 10) -> List[List[float]]:
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
            
            # Rate limiting: wait between batches
            if i + batch_size < len(texts):
                time.sleep(1)
                
        except Exception as e:
            print(f"  ⚠️ Error getting embeddings for batch {i//batch_size + 1}: {e}")
            # Fallback to individual requests with longer delays
            for text in batch:
                try:
                    emb = get_embedding(text)
                    embeddings.append(emb)
                    time.sleep(0.5)
                except Exception as e2:
                    print(f"  ❌ Failed to get embedding: {e2}")
                    # Use zero vector as fallback
                    embeddings.append([0.0] * 1536)
    
    return embeddings


def clean_query(query: str) -> str:
    """Clean the query to make it more suitable for Wikipedia search."""
    # Remove common question words
    question_words = ['what', 'is', 'are', 'who', 'when', 'where', 'why', 'how', 'does', 'do', 'did', 'can', 'could', 'would', 'should']
    
    # Split into words and filter
    words = query.lower().split()
    cleaned_words = [w.strip('?.,!;:') for w in words if w.lower() not in question_words]
    
    return ' '.join(cleaned_words) if cleaned_words else query


def search_wikipedia(query: str, max_results: int = 3) -> List[str]:
    """Search Wikipedia and return relevant article titles using MediaWiki API."""
    # Clean the query for better search results
    cleaned_query = clean_query(query)
    
    # Use MediaWiki API for search
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": cleaned_query,
        "limit": max_results,
        "format": "json"
    }
    
    headers = {
        "User-Agent": "KnowledgeRAG/1.0 (https://github.com/skepee-PROTOTYPE/knowledge-rag; educational project)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # opensearch returns: [query, [titles], [descriptions], [urls]]
        titles = data[1] if len(data) > 1 else []
        return titles
    except Exception as e:
        print(f"❌ Error searching Wikipedia: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_wikipedia_content(title: str) -> Dict[str, str]:
    """Retrieve full content from a Wikipedia article."""
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
    """Split text into overlapping chunks."""
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
    """Index a Wikipedia article in ChromaDB."""
    
    # Check if already indexed
    try:
        existing = collection.get(ids=[f"article_{article['title']}"])
        if existing['ids']:
            print(f"  ℹ️  Article '{article['title']}' already cached")
            return
    except:
        pass
    
    print(f"  📥 Indexing: {article['title']}")
    
    # Chunk the content
    chunks = chunk_text(article['content'])
    
    # Prepare data
    documents = []
    metadatas = []
    ids = []
    embeddings = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({
            "source": "wikipedia",
            "title": article["title"],
            "url": article["url"],
            "chunk_id": i
        })
        ids.append(f"{article['title']}_chunk_{i}")
    
    # Get embeddings in batches
    print(f"  🔄 Creating embeddings for {len(chunks)} chunks...")
    embeddings = get_embeddings_batch(documents, batch_size=20)
    
    # Add to collection
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )
    
    print(f"  ✅ Indexed {len(chunks)} chunks from '{article['title']}'")


def semantic_search(collection, question: str, top_k: int = 5) -> List[Dict]:
    """Search the knowledge base for relevant information."""
    
    question_embedding = get_embedding(question)
    
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )
    
    retrieved_chunks = []
    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "title": results["metadatas"][0][i]["title"],
            "url": results["metadatas"][0][i]["url"],
            "chunk_id": results["metadatas"][0][i]["chunk_id"],
            "distance": results["distances"][0][i] if "distances" in results else None
        })
    
    return retrieved_chunks


def generate_answer(question: str, retrieved_chunks: List[Dict]) -> str:
    """Generate answer using LLM with retrieved context."""
    
    # Build context with sources
    context_parts = []
    sources = {}
    
    for i, chunk in enumerate(retrieved_chunks, 1):
        title = chunk['title']
        if title not in sources:
            sources[title] = {
                'url': chunk['url'],
                'index': len(sources) + 1
            }
        
        source_idx = sources[title]['index']
        context_parts.append(f"[{source_idx}] {chunk['text']}")
    
    context = "\n\n".join(context_parts)
    
    # Build sources list
    sources_text = "\n".join([
        f"[{info['index']}] {title}: {info['url']}"
        for title, info in sources.items()
    ])
    
    prompt = f"""Answer the question based on the Wikipedia content provided below.
Include citations using [numbers] that correspond to the sources.
If the answer is not in the context, say "I don't have enough information."

Context from Wikipedia:
{context}

Question: {question}

Please provide a comprehensive answer with citations."""
    
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


def main():
    """Main function for Wikipedia RAG system."""
    
    print("=" * 70)
    print("Knowledge RAG - Wikipedia Edition")
    print("=" * 70)
    
    # Initialize ChromaDB
    chroma_client = get_persistent_client()
    collection = chroma_client.get_or_create_collection(
        name="wikipedia_knowledge",
        metadata={"description": "Wikipedia articles for RAG"}
    )
    
    print(f"\n💾 Cache loaded: {collection.count()} chunks indexed")
    print(f"📁 Cache location: {CACHE_DIR}")
    
    # Interactive Q&A loop
    print("\n🤖 Ask questions about any topic (type 'quit' to exit)")
    print("-" * 70)
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        print("\n🔍 Searching Wikipedia...")
        
        # Search Wikipedia for relevant articles
        article_titles = search_wikipedia(question, max_results=3)
        
        if not article_titles:
            print("❌ No Wikipedia articles found for this query.")
            continue
        
        print(f"📚 Found {len(article_titles)} relevant articles:")
        for title in article_titles:
            print(f"  • {title}")
        
        # Retrieve and index articles
        print("\n📥 Retrieving articles...")
        indexed_count = 0
        for title in article_titles:
            article = get_wikipedia_content(title)
            if article:
                index_wikipedia_article(collection, article)
                indexed_count += 1
        
        if indexed_count == 0:
            print("❌ Could not retrieve any articles.")
            continue
        
        # Search for relevant chunks
        print("\n🔎 Finding most relevant information...")
        retrieved_chunks = semantic_search(collection, question, top_k=5)
        
        # Generate answer
        print("💭 Generating answer...\n")
        answer, sources = generate_answer(question, retrieved_chunks)
        
        # Display answer
        print("=" * 70)
        print("📝 Answer:")
        print(answer)
        print("\n📚 Sources:")
        for title, info in sources.items():
            print(f"  [{info['index']}] {title}")
            print(f"      {info['url']}")
        print("=" * 70)


if __name__ == "__main__":
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN not found in environment variables")
        print("\n📋 Setup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Get a GitHub Personal Access Token from: https://github.com/settings/tokens")
        print("3. Add it to .env as: GITHUB_TOKEN=your_token_here")
        print("4. Run this script again")
    else:
        main()
