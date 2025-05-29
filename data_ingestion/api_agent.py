import os
import logging
import time
from typing import Dict, Any
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIAgent:
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.error("Alpha Vantage API key not found in environment variables")
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")
        self.ts = TimeSeries(key=self.api_key, output_format="pandas")
        self.fd = FundamentalData(key=self.api_key, output_format="json")

    def get_market_data(self, symbols: list) -> Dict[str, Any]:
        """Fetch market data for given symbols using Alpha Vantage."""
        try:
            data = {}
            for symbol in symbols:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        # Get daily data
                        data_df, meta_data = self.ts.get_daily(symbol, outputsize="compact")
                        latest_data = data_df.iloc[-1]  # Most recent trading day
                        data[symbol] = {
                            "price": float(latest_data["4. close"]),
                            "volume": float(latest_data["5. volume"]),
                            "market_cap": 0  # Alpha Vantage free tier does not provide market cap directly
                        }
                        break
                    except Exception as e:
                        if "API call frequency" in str(e) or "call limit" in str(e):
                            logger.warning(f"Rate limit hit for {symbol}. Retrying in {2**attempt} seconds...")
                            time.sleep(2**attempt)
                        else:
                            logger.error(f"Error fetching data for {symbol}: {str(e)}")
                            data[symbol] = {"price": 0, "volume": 0, "market_cap": 0}
                            break
                else:
                    logger.error(f"Failed to fetch data for {symbol} after retries")
                    data[symbol] = {"price": 0, "volume": 0, "market_cap": 0}
            return data
        except Exception as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return {}

    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """Fetch earnings data for a symbol using Alpha Vantage."""
        try:
            for attempt in range(3):
                try:
                    earnings_data, _ = self.fd.get_earnings_quarterly(symbol)
                    if earnings_data and len(earnings_data) > 0:
                        latest_earnings = earnings_data[0]
                        return {
                            "Reported EPS": float(latest_earnings.get("reportedEPS", 0)),
                            "Estimated EPS": float(latest_earnings.get("estimatedEPS", 0)) or 0
                        }
                    return {"Reported EPS": 0, "Estimated EPS": 0}
                except Exception as e:
                    if "API call frequency" in str(e) or "call limit" in str(e):
                        logger.warning(f"Rate limit hit for {symbol} earnings. Retrying in {2**attempt} seconds...")
                        time.sleep(2**attempt)
                    else:
                        logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
                        return {"Reported EPS": 0, "Estimated EPS": 0}
            return {"Reported EPS": 0, "Estimated EPS": 0}
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
            return {"Reported EPS": 0, "Estimated EPS": 0}