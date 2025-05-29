from data_ingestion.api_agent import APIAgent
from data_ingestion.scraping_agent import ScrapingAgent
from data_ingestion.document_loader import DocumentLoader
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent
import logging

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

    def process_query(self, query: str) -> str:
        """Process a text query and return a bullet-point narrative response."""
        try:
            if not query:
                return "No query provided."

            # Fetch market data for Asia tech stocks
            symbols = ["TSM"]  # Limit to TSMC
            market_data = self.api_agent.get_market_data(symbols)
            earnings = {symbol: self.api_agent.get_earnings(symbol) for symbol in symbols}

            # Scrape news
            news_url = "https://finance.yahoo.com/quote/TSM/news/"
            news_text = self.scraping_agent.scrape_filings(news_url)
            documents = self.document_loader.load_and_split(news_text)
            self.retriever_agent.index_documents(documents)

            # Retrieve relevant context
            retrieved_docs = self.retriever_agent.retrieve(query, k=5)
            if not retrieved_docs:
                return "Insufficient data retrieved. Please clarify your query."
            context = " ".join([doc.page_content for doc in retrieved_docs])

            # Analyze portfolio
            portfolio_weights = {"TSM": 1000000}
            exposure = self.analysis_agent.analyze_portfolio(market_data, portfolio_weights)
            earnings_surprises = {symbol: self.analysis_agent.analyze_earnings(earnings, symbol) for symbol in symbols}

            # Build bullet-point response
            bullet_points = [
                f"- **Portfolio Exposure**: {exposure:.2f}% of AUM (TSMC: ${portfolio_weights['TSM']:,.0f}).",
                f"- **TSMC (TSM)**: Price ${market_data.get('TSM', {}).get('price', 0):.2f}, Earnings Surprise {earnings_surprises.get('TSM', 0):.2f}%.",
                f"- **Market Context**: {context[:200]}..." if len(context) > 200 else f"- **Market Context**: {context}.",
                "- **Prediction**: TSMC likely to outperform due to AI demand.",
                "- **Business Strategy**: Diversify TSMC's geographic risk."
            ]
            response = "\n".join(bullet_points)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "- **Error**: An error occurred while processing your request. Please try again."
