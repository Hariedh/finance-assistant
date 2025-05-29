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
        pattern = r'\b[A-Z0-9]{1,5}(?:\.[A-Z]{1,2})?\b'
        symbols = re.findall(pattern, query.upper())
        return list(set(symbols)) if symbols else ["TSM"]

    def generate_prediction(self, market_data: dict, earnings_surprises: dict, symbols: list) -> str:
        """Generate a dynamic prediction using market data, earnings, and sector."""
        predictions = []
        for symbol in symbols:
            price = market_data.get(symbol, {}).get('price', 0)
            volume = market_data.get(symbol, {}).get('volume', 0)
            sector = market_data.get(symbol, {}).get('sector', 'Unknown')
            price_trend = market_data.get(symbol, {}).get('price_trend', 'unknown')
            earnings_surprise = earnings_surprises.get(symbol, 0)
            
            if earnings_surprise > 5 and price > 50 and volume > 1000000 and price_trend == "up":
                predictions.append(f"{symbol} ({sector}) is likely to outperform due to a strong earnings surprise of {earnings_surprise:.2f}% and an upward price trend")
            elif earnings_surprise < -5 and price_trend == "down":
                predictions.append(f"{symbol} ({sector}) may face downward pressure due to a negative earnings surprise of {earnings_surprise:.2f}% and a declining price trend")
            elif price == 0 or earnings_surprise == 0:
                predictions.append(f"{symbol} ({sector}) lacks sufficient data for a reliable prediction")
            else:
                predictions.append(f"{symbol} ({sector}) is expected to remain stable with an earnings surprise of {earnings_surprise:.2f}%")
        logger.info(f"Generated predictions: {predictions}")
        return "; ".join(predictions) + "."

    def generate_strategy(self, exposure: float, context: str, market_data: dict, symbols: list) -> str:
        """Generate a dynamic strategy using exposure, context, and market data."""
        strategies = []
        avg_price = sum(market_data.get(s, {}).get('price', 0) for s in symbols) / len(symbols) if symbols else 0
        sectors = set(market_data.get(s, {}).get('sector', 'Unknown') for s in symbols)

        # Exposure-based strategy
        if exposure > 75:
            strategies.append("Reduce exposure to diversify risk")
        elif exposure < 25:
            strategies.append("Increase exposure if fundamentals support growth")
        else:
            strategies.append("Maintain current exposure levels")

        # Sector-based strategy
        if "Technology" in sectors:
            strategies.append("Leverage growth in the technology sector")
        if "Energy" in sectors:
            strategies.append("Monitor energy sector volatility")
        if "Financials" in sectors:
            strategies.append("Assess interest rate impacts on financials")
        if len(sectors) > 3:
            strategies.append("Diversify across sectors to reduce sector-specific risk")

        # Price-based strategy
        if avg_price > 100:
            strategies.append("Monitor for potential overvaluation")
        elif avg_price < 30:
            strategies.append("Evaluate for undervaluation opportunities")

        # Context-based strategy
        if "china" in context.lower() or "geopolitical" in context.lower():
            strategies.append("Hedge against geopolitical uncertainties")
        if "supply chain" in context.lower():
            strategies.append("Strengthen supply chain resilience")
        if "ai" in context.lower() or "technology" in context.lower():
            strategies.append("Capitalize on technology sector momentum")
        if not any(keyword in context.lower() for keyword in ["china", "geopolitical", "supply chain", "ai", "technology"]):
            strategies.append("Monitor broader market trends")

        logger.info(f"Generated strategies: {strategies}")
        return "; ".join(strategies) + "."

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
            portfolio_weights = {symbol: 1000000 for symbol in symbols}
            exposure = self.analysis_agent.analyze_portfolio(market_data, portfolio_weights)
            earnings_surprises = {symbol: self.analysis_agent.analyze_earnings(earnings, symbol) for symbol in symbols}

            # Generate dynamic prediction and strategy
            prediction = self.generate_prediction(market_data, earnings_surprises, symbols)
            strategy = self.generate_strategy(exposure, context, market_data, symbols)

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
                f"- **Prediction**: {prediction}",
                f"- **Business Strategy**: {strategy}"
            ])
            response = "\n".join(bullet_points)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "- **Error**: An error occurred while processing your request. Please try again."
