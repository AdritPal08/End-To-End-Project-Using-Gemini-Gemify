import sys
from exception import CustomException
from logger import logging

import streamlit as st
import os
from pathlib import Path 
import textwrap
from PIL import Image

import google.generativeai as genai

from dotenv import load_dotenv
env_loaded = load_dotenv() # take environment variables from .env.
if env_loaded:
    logging.info("Environment variables loaded.")
else:
    logging.error("Environment variables not loaded.")

# api_key = os.getenv("GOOGLE_API_KEY")
api_key = st.secrets["GOOGLE_API_KEY"]
if api_key:
    genai.configure(api_key=api_key)
else:
    logging.error("API key not found or empty.")

def to_markdown(text):
  # Remove the indentation from the text
  text = textwrap.dedent(text)
  # Add the markdown syntax manually
  text = "#" "\n" + text.replace("•", "*")
  # Return the markdown-formatted string
  return text

## Function to load OpenAI model and get respones
def get_gemini_response(text_prompt,image):
    try: 
        # You need to use the genai module to access the generativeai model
        model =  genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([text_prompt,image])
        response.resolve()
        final_response = to_markdown(response.text)
        logging.info("Response generated.")
        return final_response # return the markdown-formatted string
    except Exception as e:
        raise CustomException(e,sys)

# initialize our streamlit app
st.set_page_config(page_title="Gemify")
logging.info("Streamlit app initialized.")

st.header("Gemify Application")
st.write("An app that transforms your photos and texts into creative content.")

# Create a sidebar
sidebar = st.sidebar

# Get the text prompt from the user
input = sidebar.text_input("Text Prompt: ", key="input")
logging.info(f"User input: {input}")

# Get the image from the user
uploaded_file = sidebar.file_uploader("Choose an Image: ", type=["jpg", "jpeg", "png"])
image=""   
if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        sidebar.image(image, caption="Uploaded Image.", use_column_width=True) # display the image in the sidebar
    except IOError as e:
        logging.error(e)
        sidebar.error(f"An error occurred: {e}")

# Get the output format from the user
output_format = sidebar.radio("Output Format: ", options=["Markdown", "Plain Text"], index=0)

# Create an animated button with an emoji
button_css = st.markdown("""
<style>
@keyframes pulse {
  0% {
    transform: scale(0.95);
  }
  70% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(0.95);
  }
}
.stButton>button {
  animation: pulse 2s infinite;
  font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

submit=st.button("👉 Tell me..", key="submit")

## If ask button is clicked

if submit:
    try:
        # Create a spinner object
        with st.spinner('Generating response...'):
            # Do some computation here
            response = get_gemini_response(input, image)
            # Display the response
            st.subheader("The Response is")
            if output_format == "Markdown":
                st.write(response) # display the response as markdown
            else:
                st.text(response) # display the response as plain text
            # Create a download button
            st.download_button(
                label="Download the response",
                data=response,
                file_name="response.md",
                mime="text/markdown"
            )
    except CustomException as e:
        # handle the custom exception
        logging.error(e) # log the error information
        st.error(f"An error occurred: {e.message}") # display the error message in the streamlit app
    except Exception as e:
        # handle any other exception
        logging.error(e)
        st.error(f"An error occurred: {e}")
# Add a footer with your name
footer_css = st.markdown("""
<style>
.footer {
  position: fixed;
  bottom: 0;
  right: 0;
  padding: 10px;
  color: white;
  font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

footer = st.markdown("""
<div class="footer">
Created by : Adrit Pal
</div>
""", unsafe_allow_html=True)
