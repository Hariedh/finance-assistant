# Multi-Agent Finance Assistant

A Streamlit-based finance assistant delivering text-based market briefs for Asia tech stocks using a multi-agent architecture.

## Architecture
- **API Agent**: Fetches market data via yfinance.
- **Scraping Agent**: Crawls financial news using BeautifulSoup.
- **Document Loader**: Splits text for embedding using LangChain.
- **Retriever Agent**: Indexes and retrieves using FAISS and HuggingFace embeddings.
- **Analysis Agent**: Computes portfolio exposure and earnings surprises.
- **Language Agent**: Generates narratives using distilgpt2.
- **Orchestrator**: Coordinates agents within the Streamlit app.

## Setup
1. Clone the repository: `git clone <repo_url>`
2. Install dependencies locally:
   ```bash
   pip install -r requirements.txt
   python streamlit_app/app.py
   ```
3. Access the app at `http://localhost:8501`.

## Deployment
Deployed on Streamlit Cloud: [URL to be added after deployment]

## Performance
- **Latency**: ~2s for text queries.
- **RAG Accuracy**: Top-5 retrieval with FAISS.
- **Scalability**: Lightweight models (distilgpt2) for low resource usage.

## Framework Comparisons
- **yfinance vs AlphaVantage**: yfinance chosen for free, unlimited access.
- **FAISS vs Pinecone**: FAISS for local, cost-free vector storage.
- **distilgpt2 vs larger LLMs**: Lightweight for deployment; larger models improve narrative but increase latency.

## Usage
- Enter a query like "What's our risk exposure in Asia tech stocks today?".
- The system responds with a narrative, e.g., "Today, your Asia tech allocation is 55.56% of AUM, up from yesterday. TSMC beat estimates by 4%, Samsung missed by 2%."