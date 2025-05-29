import logging
import streamlit as st
import sys
import os
import tempfile
from gtts import gTTS

# Add root and subdirectories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../orchestrator')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data_ingestion')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../agents')))

from orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_audio(text: str, output_path: str) -> bool:
    """Generate audio from text using gTTS."""
    try:
        clean_text = text.replace('- **', '').replace('**:', ':').replace('\n', '. ')
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(output_path)
        logger.info(f"Audio generated and saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return False

# Initialize orchestrator
orchestrator = Orchestrator()

st.title("Morning Market Brief")
st.markdown("Ask about your stock portfolio.")

# Text inputs
symbols_input = st.text_input("Enter stock symbols (comma-separated, e.g., TSM, AAPL, NVDA)", value="TSM")
query = st.text_input("Enter your query (e.g., What's our risk exposure in stocks today?)")

if st.button("Submit"):
    try:
        if not query or not symbols_input:
            st.error("Please provide both stock symbols and a query.")
        else:
            # Parse symbols from input
            symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
            if not symbols:
                st.error("Please provide at least one valid stock symbol.")
            else:
                # Process query with symbols
                response = orchestrator.process_query(query, symbols)
                logger.info(f"Generated response: {response}")
                # Display response as markdown
                st.success("Response received!")
                st.markdown(response, unsafe_allow_html=True)
                # Generate and play audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    if generate_audio(response, temp_audio.name):
                        st.audio(temp_audio.name, format="audio/mp3", start_time=0)
                        os.remove(temp_audio.name)  # Clean up
                    else:
                        st.warning("Failed to generate audio response.")
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error(f"An error occurred: {str(e)}. Please try again.")
