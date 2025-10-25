# Knowledge RAG

A Retrieval-Augmented Generation (RAG) system that interfaces with public knowledge sources to provide intelligent, context-aware answers with citations.

## 🚀 Features

- **Wikipedia Integration**: Query and retrieve information from Wikipedia in real-time
- **Semantic Search**: Uses vector embeddings for accurate information retrieval
- **Persistent Caching**: ChromaDB storage for faster repeated queries
- **Source Citations**: All answers include Wikipedia article references
- **Expandable**: Architecture supports adding more knowledge sources (ArXiv, PubMed, etc.)

## 📋 Current Knowledge Sources

- ✅ Wikipedia
- 🔜 ArXiv (planned)
- 🔜 PubMed (planned)
- 🔜 Custom documents (planned)

## 🛠️ Technology Stack

- **LLM**: GPT-4.1-mini via GitHub Models (free tier)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: ChromaDB (persistent)
- **Knowledge Source**: Wikipedia API
- **Language**: Python 3.9+

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/skepee-PROTOTYPE/knowledge-rag.git
cd knowledge-rag
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN
```

4. Get a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Create a new token with appropriate permissions
   - Add it to your `.env` file

## 🎯 Usage

### Basic Wikipedia RAG

```bash
python wiki_rag.py
```

Then ask questions like:
- "What is quantum computing?"
- "Explain the theory of relativity"
- "Who was Alan Turing?"

### Access the Knowledge Database

```bash
python access_db.py
```

## 📁 Project Structure

```
knowledge-rag/
├── wiki_rag.py          # Main Wikipedia RAG implementation
├── access_db.py         # Database inspection tool
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── cache/              # ChromaDB cache (gitignored)
```

## 🔧 Configuration

Edit `.env` to configure:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token
- `CACHE_DIR`: ChromaDB cache location (default: `./cache`)
- `MAX_CACHE_SIZE`: Maximum cached articles (default: 100)

## 🎓 How It Works

1. **Query Processing**: User asks a question
2. **Wikipedia Search**: Find relevant articles via Wikipedia API
3. **Content Retrieval**: Download and chunk article content
4. **Embedding**: Generate vector embeddings for chunks
5. **Caching**: Store in ChromaDB for future queries
6. **Semantic Search**: Find most relevant chunks
7. **Answer Generation**: LLM generates answer with citations

## 🚧 Roadmap

- [x] Wikipedia integration
- [ ] ArXiv paper search
- [ ] PubMed medical literature
- [ ] Multi-source queries
- [ ] Web UI
- [ ] API endpoint
- [ ] Advanced caching strategies

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

Project Link: https://github.com/skepee-PROTOTYPE/knowledge-rag
