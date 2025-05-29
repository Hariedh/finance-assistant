import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    def analyze_portfolio(self, market_data: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate portfolio exposure."""
        try:
            total_value = sum(weights.get(symbol, 0) * data.get("price", 0) for symbol, data in market_data.items())
            aum = sum(weights.values())
            exposure = (total_value / aum * 100) if aum > 0 else 0
            # Cap exposure at 100% to avoid calculation errors
            return min(exposure, 100.0)
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            return 0

    def analyze_earnings(self, earnings: Dict[str, Any], symbol: str) -> float:
        """Calculate earnings surprise."""
        try:
            actual = earnings.get(symbol, {}).get("Reported EPS", 0)
            estimate = earnings.get(symbol, {}).get("Estimated EPS", 0)
            return ((actual - estimate) / estimate * 100) if estimate != 0 else 0
        except Exception as e:
            logger.error(f"Error analyzing earnings for {symbol}: {str(e)}")
            return 0