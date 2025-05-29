import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    def analyze_portfolio(self, market_data: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate portfolio exposure as a percentage of total AUM."""
        try:
            total_aum = sum(weights.values())
            if total_aum == 0:
                logger.warning("Total AUM is zero, cannot calculate exposure")
                return 0.0

            exposure_value = 0
            for symbol, weight in weights.items():
                price = market_data.get(symbol, {}).get("price", 0)
                exposure_value += weight * price
            exposure = (exposure_value / total_aum) * 100 if total_aum > 0 else 0
            logger.info(f"Portfolio exposure calculated: {exposure:.2f}%")
            return exposure
        except Exception as e:
            logger.error(f"Error calculating portfolio exposure: {str(e)}")
            return 0.0

    def analyze_earnings(self, earnings: Dict[str, Dict[str, float]], symbol: str) -> float:
        """Calculate earnings surprise percentage for a symbol."""
        try:
            earnings_data = earnings.get(symbol, {})
            reported_eps = earnings_data.get("Reported EPS", 0)
            estimated_eps = earnings_data.get("Estimated EPS", 0)
            if estimated_eps == 0:
                logger.warning(f"Estimated EPS for {symbol} is zero, cannot calculate surprise")
                return 0.0
            surprise = ((reported_eps - estimated_eps) / estimated_eps) * 100
            logger.info(f"Earnings surprise for {symbol}: {surprise:.2f}% (Reported: {reported_eps}, Estimated: {estimated_eps})")
            return surprise
        except Exception as e:
            logger.error(f"Error calculating earnings surprise for {symbol}: {str(e)}")
            return 0.0
