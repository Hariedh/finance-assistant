from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageAgent:
    def __init__(self):
        try:
            self.generator = pipeline("text-generation", model="distilgpt2")
        except Exception as e:
            logger.error(f"Error initializing language model: {str(e)}")
            self.generator = None

    def generate_narrative(self, context: str, query: str) -> str:
        """Generate a narrative response based on context and query."""
        try:
            if self.generator:
                prompt = f"Based on the following context: {context}\n\nAnswer the query: {query}"
                # Truncate input to avoid exceeding max_length
                response = self.generator(
                    prompt,
                    max_new_tokens=100,  # Generate up to 100 new tokens
                    truncation=True,
                    pad_token_id=50256,
                    num_return_sequences=1
                )[0]["generated_text"]
                return response.strip()
            return "Unable to generate narrative due to model unavailability."
        except Exception as e:
            logger.error(f"Error generating narrative: {str(e)}")
            return "Error generating response."