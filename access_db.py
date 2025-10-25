"""
Database Access Tool
View and query the cached Wikipedia knowledge base.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import chromadb

load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN")
)

CACHE_DIR = os.environ.get("CACHE_DIR", "./cache")


def get_embedding(text: str):
    """Get embedding for search."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def main():
    """Main function to access the knowledge database."""
    
    # Check if cache exists
    if not Path(CACHE_DIR).exists():
        print(f"❌ Cache not found at {CACHE_DIR}")
        print("Run wiki_rag.py first to create the cache!")
        return
    
    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path=CACHE_DIR)
    
    print("=" * 70)
    print("Knowledge Database Browser")
    print("=" * 70)
    
    # List collections
    collections = chroma_client.list_collections()
    
    if not collections:
        print("\n❌ No collections found in database.")
        return
    
    print(f"\n📚 Collections: {len(collections)}")
    for col in collections:
        print(f"  • {col.name}: {col.count()} documents")
    
    # Get wikipedia_knowledge collection
    try:
        collection = chroma_client.get_collection("wikipedia_knowledge")
    except:
        print("\n❌ 'wikipedia_knowledge' collection not found.")
        return
    
    print(f"\n🔍 Collection: {collection.name}")
    print(f"📊 Total chunks: {collection.count()}")
    
    # Get all articles
    results = collection.get()
    
    # Extract unique articles
    articles = {}
    for metadata in results['metadatas']:
        title = metadata['title']
        if title not in articles:
            articles[title] = {
                'url': metadata['url'],
                'chunks': 0
            }
        articles[title]['chunks'] += 1
    
    print(f"\n📄 Cached Wikipedia Articles: {len(articles)}")
    for i, (title, info) in enumerate(articles.items(), 1):
        print(f"\n  [{i}] {title}")
        print(f"      URL: {info['url']}")
        print(f"      Chunks: {info['chunks']}")
    
    # Interactive search
    print("\n" + "=" * 70)
    print("🔎 Search Mode - Enter a query to search cached knowledge")
    print("Type 'quit' to exit")
    print("-" * 70)
    
    while True:
        query = input("\n🔍 Search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        # Search
        query_embedding = get_embedding(query)
        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        print(f"\n📊 Top 5 Results for: '{query}'")
        print("-" * 70)
        
        for i in range(len(search_results["documents"][0])):
            doc = search_results["documents"][0][i]
            meta = search_results["metadatas"][0][i]
            distance = search_results["distances"][0][i]
            
            similarity = 1 - distance
            
            print(f"\n  Result {i + 1}:")
            print(f"  Title: {meta['title']}")
            print(f"  Similarity: {similarity:.4f}")
            print(f"  Text Preview: {doc[:200]}...")
            print(f"  URL: {meta['url']}")


if __name__ == "__main__":
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN not found")
        print("Please set GITHUB_TOKEN in .env file")
    else:
        main()
