from gtts import gTTS
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_audio(text: str, output_path: str) -> bool:
    """Generate audio from text using gTTS and save to output_path."""
    try:
        # Convert bullet points to natural speech
        clean_text = text.replace("- **", "").replace("**:", ":").replace("\n", ". ")
        tts = gTTS(text=clean_text, lang="en", slow=False)
        tts.save(output_path)
        logger.info(f"Audio generated and saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return False