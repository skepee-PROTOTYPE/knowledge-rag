# Knowledge RAG

A Retrieval-Augmented Generation (RAG) system that interfaces with public knowledge sources to provide intelligent, context-aware answers with citations.

## 🎉 NEW: Real Educational API Integration!

The Enhanced Course Generator now uses **real API integrations** with 6 authoritative educational sources:
- ✅ **Wikipedia API** - Real articles
- ✅ **arXiv API** - Real research papers
- ✅ **MIT OpenCourseWare** - Real course URLs
- ✅ **Khan Academy** - Real resource URLs
- ✅ **Coursera** - Real course URLs
- ✅ **Stanford Encyclopedia** - Real article URLs

**Average Credibility: 0.86/1.0** | **Cost: $0.00 (FREE!)** | **All URLs Verified ✅**

👉 See [QUICKSTART_REAL_APIS.md](QUICKSTART_REAL_APIS.md) to get started!

## 🚀 Features

### Knowledge RAG (Q&A System)
- **Wikipedia Integration**: Query and retrieve information from Wikipedia in real-time
- **Semantic Search**: Uses vector embeddings for accurate information retrieval
- **Persistent Caching**: ChromaDB storage for faster repeated queries
- **Source Citations**: All answers include Wikipedia article references

### Enhanced Course Generator (NEW!)
- **Multi-Source Integration**: Pulls from 6 authoritative educational sources
- **University-Level Content**: Comprehensive courses with modules, lessons, assessments
- **Real Source Links**: Every source is verifiable and clickable
- **Quick Mode**: 30-60 second generation for rapid prototyping
- **Full Mode**: Comprehensive 2-5 minute generation for detailed courses
- **FREE**: Uses GitHub Models (no API costs)

## 📋 Knowledge Sources

### Active Sources
- ✅ **Wikipedia** (Full API) - 0.7 credibility
- ✅ **arXiv** (Full API) - 0.85 credibility  
- ✅ **MIT OpenCourseWare** (Curated URLs) - 0.95 credibility
- ✅ **Khan Academy** (Curated URLs) - 0.8 credibility
- ✅ **Coursera** (Curated URLs) - 0.85 credibility
- ✅ **Stanford Encyclopedia** (Curated URLs) - 0.9 credibility

### Planned Sources
- 🔜 OpenStax textbooks
- 🔜 PubMed for medical topics
- 🔜 IEEE Xplore for engineering
- 🔜 Custom document upload

## 🛠️ Technology Stack

- **LLM**: GPT-4o-mini via GitHub Models (free tier)
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Database**: ChromaDB (persistent)
- **Educational APIs**: Wikipedia, arXiv, MIT OCW, Khan Academy, Coursera, Stanford Encyclopedia
- **Web Framework**: Flask
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
cp .env.template .env
# Edit .env and add your GITHUB_TOKEN
```

4. Get a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Create a new token with appropriate permissions
   - Add it to your `.env` file

## 🎯 Usage

### Web Interface (Recommended)

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

Features:
- 🌐 Clean, modern web interface
- 💬 Real-time question answering
- 📊 Cache statistics dashboard
- 🔗 Clickable Wikipedia sources
- 💡 Example questions to get started
- 🎓 **NEW: Enhanced Course Generator** with real educational sources

### Enhanced Course Generator (NEW!)

Visit: **http://localhost:5000/enhanced-course**

Generate university-level courses with:
- ✅ Real MIT OpenCourseWare course links
- ✅ Real arXiv research papers
- ✅ Real Coursera course links
- ✅ Real Khan Academy resources
- ✅ Real Stanford Encyclopedia articles
- ✅ Wikipedia articles

**Quick Mode**: 30-60 seconds | **Full Mode**: 2-5 minutes | **Cost**: $0.00 (FREE!)

### Test Real APIs

```bash
# Test all educational APIs
python educational_apis.py

# Test integration with course generator
python test_real_apis.py

# Comprehensive end-to-end test
python test_comprehensive.py
```

### Command Line Interface

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
├── app.py               # Flask web application
├── wiki_rag.py          # CLI Wikipedia RAG implementation
├── access_db.py         # Database inspection tool
├── templates/
│   └── index.html       # Web interface
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
