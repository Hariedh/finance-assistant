import logging
import streamlit as st
import sys
import os

# Add parent directory and subdirectories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../orchestrator')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data_ingestion')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../agents')))

from orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            # Display response as markdown to render bullet points
            st.success("Response received!")
            st.markdown(response, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Error in Streamlit app: {str(e)}")
        st.error("An error occurred. Please try again.")