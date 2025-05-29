import logging
import streamlit as st
import sys
import os.path
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
        # Convert bullet points to natural speech
        clean_text = text.replace('- **', '').replace('**:', ':').replace('\n', '. ')
        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(output_path)
        logger.info(f'Audio generated and saved to {output_path}')
        return True
    except Exception as e:
        logger.error(f'Error generating audio: {str(e)}')
        return False

# Initialize orchestrator
orchestrator = Orchestrator()

st.title("Morning Market Brief")
st.markdown("Ask about your Asia tech portfolio.")

# Text input
query = st.text_input("Enter your query (e.g., What's our risk exposure in Asia tech stocks today?)")

if st.button("Submit"):
    try:
        if not query:
            st.error("No query provided.")
        else:
            # Process query
            response = orchestrator.process_query(query)
            # Display response as markdown
            st.success("Response received!")
            st.markdown(response, unsafe_text=True)
            # Generate and play audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                if generate_audio(response, temp_audio.name):
                    st.audio(temp_audio.name, format="audio/mp3", start_time=0)
                    os.remove(temp_audio.name)  # Clean up
                else:
                    st.warning("Failed to generate audio response.")
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error("An error occurred. Please try again.")
