# AI Tool Usage

This document outlines the AI tools used in the Multi-Agent Finance Assistant.

## yfinance
- **Purpose**: Fetches real-time market data and earnings for Asia tech stocks (e.g., TSMC, Samsung).
- **Usage**: APIAgent retrieves price, volume, market cap, and earnings data.
- **Justification**: Free, reliable, and supports multiple exchanges.

## BeautifulSoup
- **Purpose**: Scrapes financial news from websites (e.g., Yahoo Finance).
- **Usage**: ScrapingAgent extracts news text for context.
- **Justification**: Lightweight and effective for HTML parsing.

## LangChain
- **Purpose**: Splits news text into chunks for embedding.
- **Usage**: DocumentLoader processes text for FAISS indexing.
- **Justification**: Simplifies text preprocessing for RAG.

## FAISS
- **Purpose**: Indexes and retrieves relevant news snippets.
- **Usage**: RetrieverAgent uses FAISS with HuggingFace embeddings.
- **Justification**: Fast, local vector store with no external costs.

## HuggingFace (sentence-transformers)
- **Purpose**: Generates embeddings for news text.
- **Usage**: RetrieverAgent embeds text using all-MiniLM-L6-v2.
- **Justification**: Lightweight and accurate for semantic search.

## HuggingFace (distilgpt2)
- **Purpose**: Generates narrative responses.
- **Usage**: LanguageAgent produces human-readable answers.
- **Justification**: Small model suitable for deployment with low latency.