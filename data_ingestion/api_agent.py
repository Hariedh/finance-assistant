import os
import logging
import time
from typing import Dict, Any, List
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
        self.rate_limit_delay = 12  # 5 calls/minute = 12s delay

    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid by attempting a lightweight API call."""
        try:
            data, _ = self.ts.get_symbol_search(keywords=symbol)
            return not data.empty
        except Exception as e:
            logger.warning(f"Symbol validation failed for {symbol}: {str(e)}")
            return False

    def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch market data for given symbols using Alpha Vantage."""
        try:
            data = {}
            valid_symbols = [s for s in symbols if self.validate_symbol(s)]
            if not valid_symbols:
                logger.error("No valid symbols provided")
                return {}

            for symbol in valid_symbols:
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        # Get daily data
                        data_df, meta_data = self.ts.get_daily(symbol, outputsize="compact")
                        if not data_df.empty:
                            latest_data = data_df.iloc[-1]  # Most recent trading day
                            data[symbol] = {
                                "price": float(latest_data["4. close"]),
                                "volume": float(latest_data["5. volume"]),
                                "market_cap": 0  # Free tier limitation
                            }
                        else:
                            data[symbol] = {"price": 0, "volume": 0, "market_cap": 0}
                        break
                    except Exception as e:
                        if "API call frequency" in str(e) or "call limit" in str(e):
                            logger.warning(f"Rate limit hit for {symbol}. Retrying in {2**attempt} seconds...")
                            time.sleep(2**attempt)
                        else:
                            logger.error(f"Error fetching data for {symbol}: {str(e)}")
                            data[symbol] = {"price": 0, "volume": 0, "market_cap": 0}
                            break
                    time.sleep(self.rate_limit_delay)  # Throttle API calls
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
            if not self.validate_symbol(symbol):
                logger.warning(f"Invalid symbol {symbol} for earnings")
                return {"Reported EPS": 0, "Estimated EPS": 0}

            for attempt in range(3):
                try:
                    earnings_data, _ = self.fd.get_earnings_quarterly(symbol)
                    if isinstance(earnings_data, list) and len(earnings_data) > 0:
                        latest_earnings = earnings_data[0]
                        return {
                            "Reported EPS": float(latest_earnings.get("reportedEPS", 0) or 0),
                            "Estimated EPS": float(latest_earnings.get("estimatedEPS", 0) or 0)
                        }
                    logger.warning(f"No earnings data returned for {symbol}")
                    return {"Reported EPS": 0, "Estimated EPS": 0}
                except Exception as e:
                    if "API call frequency" in str(e) or "call limit" in str(e):
                        logger.warning(f"Rate limit hit for {symbol} earnings. Retrying in {2**attempt} seconds...")
                        time.sleep(2**attempt)
                    else:
                        logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
                        return {"Reported EPS": 0, "Estimated EPS": 0}
                time.sleep(self.rate_limit_delay)
            logger.error(f"Failed to fetch earnings for {symbol} after retries")
            return {"Reported EPS": 0, "Estimated EPS": 0}
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {str(e)}")
            return {"Reported EPS": 0, "Estimated EPS": 0}
