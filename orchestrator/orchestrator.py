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

    def extract_symbols(self, text: str) -> list:
        """Extract and validate stock symbols from text."""
        # Regex to match stock symbols: 2-5 uppercase letters, optionally followed by numbers and/or a dot with 1-2 letters
        pattern = r'\b[A-Z]{2,5}(?:[0-9]+)?(?:\.[A-Z]{1,2})?\b'
        potential_symbols = re.findall(pattern, text)
        if not potential_symbols:
            logger.info("No symbols found, using default symbol TSM")
            return ["TSM"]

        # Validate symbols
        valid_symbols = []
        for symbol in potential_symbols:
            if self.api_agent.validate_symbol(symbol):
                valid_symbols.append(symbol)
            else:
                logger.warning(f"Symbol {symbol} is invalid and will be skipped")

        if not valid_symbols:
            logger.info("No valid symbols found, using default symbol TSM")
            return ["TSM"]

        logger.info(f"Valid symbols extracted: {valid_symbols}")
        return list(set(valid_symbols))

    def generate_prediction(self, market_data: dict, earnings_surprises: dict, symbols: list) -> str:
        """Generate a dynamic prediction using market data, earnings, and sector."""
        predictions = []
        for symbol in symbols:
            price = market_data.get(symbol, {}).get('price', 0)
            volume = market_data.get(symbol, {}).get('volume', 0)
            sector = market_data.get(symbol, {}).get('sector', 'Unknown')
            price_trend = market_data.get(symbol, {}).get('price_trend', 'unknown')
            market_cap = market_data.get(symbol, {}).get('market_cap', 0)
            earnings_surprise = earnings_surprises.get(symbol, 0)

            # Categorize stock by market cap
            if market_cap > 200e9:
                cap_category = "large-cap"
            elif market_cap > 10e9:
                cap_category = "mid-cap"
            else:
                cap_category = "small-cap"

            # Dynamic prediction logic
            if earnings_surprise > 5 and price > 50 and volume > 500000 and price_trend == "up":
                predictions.append(f"{symbol} ({sector}, {cap_category}) is poised to outperform with a strong earnings surprise of {earnings_surprise:.2f}% and upward momentum")
            elif earnings_surprise < -5 and price_trend == "down":
                predictions.append(f"{symbol} ({sector}, {cap_category}) may underperform due to a negative earnings surprise of {earnings_surprise:.2f}% and downward momentum")
            elif price == 0 or earnings_surprise == 0 or volume == 0:
                predictions.append(f"{symbol} ({sector}, {cap_category}) lacks sufficient data for a reliable prediction")
            elif volume < 100000:
                predictions.append(f"{symbol} ({sector}, {cap_category}) may see limited movement due to low trading volume")
            else:
                predictions.append(f"{symbol} ({sector}, {cap_category}) is likely to remain stable with an earnings surprise of {earnings_surprise:.2f}%")
        logger.info(f"Generated predictions: {predictions}")
        return "; ".join(predictions) + "."

    def generate_strategy(self, exposure: float, context: str, market_data: dict, symbols: list) -> str:
        """Generate a dynamic strategy using exposure, context, and market data."""
        strategies = []
        avg_price = sum(market_data.get(s, {}).get('price', 0) for s in symbols) / len(symbols) if symbols else 0
        sectors = set(market_data.get(s, {}).get('sector', 'Unknown') for s in symbols)
        trends = [market_data.get(s, {}).get('price_trend', 'unknown') for s in symbols]
        upward_trends = trends.count("up")
        downward_trends = trends.count("down")

        # Exposure-based strategy
        if exposure > 75:
            strategies.append("Reduce exposure to diversify risk")
        elif exposure < 25:
            strategies.append("Increase exposure if fundamentals support growth")
        else:
            strategies.append("Maintain current exposure levels")

        # Trend-based strategy
        if upward_trends > len(symbols) / 2:
            strategies.append("Consider riding the upward momentum")
        elif downward_trends > len(symbols) / 2:
            strategies.append("Prepare for potential downside risks")

        # Sector-based strategy
        if "Technology" in sectors:
            strategies.append("Leverage growth opportunities in technology")
        if "Energy" in sectors:
            strategies.append("Monitor energy sector volatility due to global factors")
        if "Financials" in sectors:
            strategies.append("Assess interest rate impacts on financial stocks")
        if len(sectors) > 3:
            strategies.append("Maintain sector diversification to mitigate risks")
        elif len(sectors) == 1:
            strategies.append("Diversify across sectors to reduce concentration risk")

        # Price-based strategy
        if avg_price > 100:
            strategies.append("Watch for overvaluation risks")
        elif avg_price < 30:
            strategies.append("Explore undervaluation opportunities")

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

    def process_query(self, query: str, symbols: list) -> str:
        """Process a text query and return a bullet-point narrative response."""
        try:
            if not query:
                return "No query provided."
            if not symbols:
                return "No symbols provided."

            # Use provided symbols
            valid_symbols = symbols
            logger.info(f"Processing symbols: {valid_symbols}")

            # Fetch market data
            market_data = self.api_agent.get_market_data(valid_symbols)
            earnings = {symbol: self.api_agent.get_earnings(symbol) for symbol in valid_symbols}

            # Scrape news for first valid symbol
            news_url = f"https://finance.yahoo.com/quote/{valid_symbols[0]}/news/"
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
            portfolio_weights = {symbol: 1000000 for symbol in valid_symbols}
            exposure = self.analysis_agent.analyze_portfolio(market_data, portfolio_weights)
            earnings_surprises = {symbol: self.analysis_agent.analyze_earnings(earnings, symbol) for symbol in valid_symbols}

            # Generate dynamic prediction and strategy
            prediction = self.generate_prediction(market_data, earnings_surprises, valid_symbols)
            strategy = self.generate_strategy(exposure, context, market_data, valid_symbols)

            # Build bullet-point response
            bullet_points = [
                f"- **Portfolio Exposure**: {exposure:.2f}% of AUM ({', '.join([f'{s}: ${portfolio_weights[s]:,.0f}' for s in valid_symbols])})."
            ]
            for symbol in valid_symbols:
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
            logger.info(f"Generated response: {response}")
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "- **Error**: An error occurred while processing your request. Please try again."
