from data_ingestion.api_agent import APIAgent
from data_ingestion.scraping_agent import ScrapingAgent
from data_ingestion.document_loader import DocumentLoader
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.api_agent = APIAgent()
        self.scraping_agent = ScrapingAgent()
        self.document_loader = DocumentLoader()
        self.retriever_agent = RetrieverAgent()
        self.analysis_agent = AnalysisAgent()
        self.language_agent = LanguageAgent()

    def extract_symbols(self, query: str) -> list:
        """Extract stock symbols from query using regex."""
        # Match uppercase letters/numbers (e.g., TSM, AAPL, 005930.KS)
        pattern = r'\b[A-Z0-9]{1,5}(?:\.[A-Z]{1,2})?\b'
        symbols = re.findall(pattern, query.upper())
        return list(set(symbols)) if symbols else ["TSM"]  # Default to TSM if none found

    def process_query(self, query: str) -> str:
        """Process a text query and return a bullet-point narrative response."""
        try:
            if not query:
                return "No query provided."

            # Extract symbols from query
            symbols = self.extract_symbols(query)
            logger.info(f"Processing symbols: {symbols}")

            # Fetch market data
            market_data = self.api_agent.get_market_data(symbols)
            earnings = {symbol: self.api_agent.get_earnings(symbol) for symbol in symbols}

            # Scrape news for first valid symbol
            news_url = f"https://finance.yahoo.com/quote/{symbols[0]}/news/"
            news_text = self.scraping_agent.scrape_filings(news_url)
            documents = self.document_loader.load_and_split(news_text)
            self.retriever_agent.index_documents(documents)

            # Retrieve relevant context
            retrieved_docs = self.retriever_agent.retrieve(query, k=5)
            if not retrieved_docs:
                context = "No relevant news found."
            else:
                context = " ".join([doc.page_content for doc in retrieved_docs])

            # Analyze portfolio
            portfolio_weights = {symbol: 1000000 for symbol in symbols}  # Equal weights
            exposure = self.analysis_agent.analyze_portfolio(market_data, portfolio_weights)
            earnings_surprises = {symbol: self.analysis_agent.analyze_earnings(earnings, symbol) for symbol in symbols}

            # Build bullet-point response
            bullet_points = [
                f"- **Portfolio Exposure**: {exposure:.2f}% of AUM ({', '.join([f'{s}: ${portfolio_weights[s]:,.0f}' for s in symbols])})."
            ]
            for symbol in symbols:
                bullet_points.append(
                    f"- **{symbol}**: Price ${market_data.get(symbol, {}).get('price', 0):.2f}, "
                    f"Earnings Surprise {earnings_surprises.get(symbol, 0):.2f}%."
                )
            bullet_points.extend([
                f"- **Market Context**: {context[:200]}..." if len(context) > 200 else f"- **Market Context**: {context}.",
                "- **Prediction**: Stocks with strong AI exposure likely to outperform.",
                "- **Business Strategy**: Diversify geographic risks and monitor earnings."
            ])
            response = "\n".join(bullet_points)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "- **Error**: An error occurred while processing your request. Please try again."
