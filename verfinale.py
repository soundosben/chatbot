import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Configure Streamlit page settings with custom colors
st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon="🤖",  # Robot emoji
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    },
)

# Background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFC1E0; /* Light Barbie pink background color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

# Paths to your PDF files
pdf_path_fr = "D:/Banque_FR.pdf"
pdf_path_ar = "D:/Banque_AR.pdf"

# Load PDF content for both files
pdf_text_fr = extract_text_from_pdf(pdf_path_fr)
pdf_text_ar = extract_text_from_pdf(pdf_path_ar)

# Initialize chat session without context
model = gen_ai.GenerativeModel('gemini-pro')
chat_session = model.start_chat(history=[])

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Display the chatbot's title on the page with custom color and font
st.title("🤖 Chat Bot!")
st.markdown(
    """
    <style>
    .stApp h1 {
        color: #000000; /* Title color */
        font-size: 60px; /* Title font size */
        text-align: center; /* Title alignment */
        margin-bottom: 30px; /* Bottom margin */
        font-family: 'Pacifico', cursive; /* Custom font */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the chat history with bold font for questions and responses
for message in chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        if message.role == "user":
            st.markdown(f"{message.parts[0].text}")
        else:
            st.markdown(f"{message.parts[0].text}", unsafe_allow_html=True)

# Input field for user's message with custom color
user_prompt = st.text_input("Ask Chat Bot...", key="user_input")
st.markdown(
    """
    <style>
    .stTextField>div>div>input {
        color: #000000; /* Text color */
        background-color: #FFD700; /* Input field background color */
        border-color: #FF5733; /* Border color */
        border-width: 2px;
        border-radius: 10px;
        padding: 10px; /* Padding */
        font-size: 16px; /* Input field font size */
        font-family: 'Roboto', sans-serif; /* Custom font */
    }
    </style>
    """,
    unsafe_allow_html=True
)

if user_prompt:
    # Concatenate user's message with PDF contents as context
    user_with_context = f"{pdf_text_fr}\n{pdf_text_ar}\n{user_prompt}"
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Send user's message with context to Gemini-Pro and get the response
    gemini_response = chat_session.send_message(user_with_context)

    # Check if Gemini-Pro's response is empty (meaning the answer wasn't found in the PDF)
    if gemini_response.text.strip() == "Cette question n'est pas abordée dans le contexte fourni.":
        # If the response is empty, send the user's question directly to Gemini-Pro
        gemini_response = chat_session.send_message(user_prompt)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(f"{gemini_response.text}", unsafe_allow_html=True)