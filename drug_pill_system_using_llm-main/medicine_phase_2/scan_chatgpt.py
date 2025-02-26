import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv
import tempfile
import os
from PIL import Image
import google.generativeai as genai
import base64
import re
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state variables
if 'audio_file_path' not in st.session_state:
    st.session_state.audio_file_path = None
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'response' not in st.session_state:
    st.session_state.response = ""
if 'previous_language' not in st.session_state:
    st.session_state.previous_language = "English"
if 'previous_input_method' not in st.session_state:
    st.session_state.previous_input_method = "Upload Image"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to get response from Gemini model
def get_gemini_response(input_text, image=None, prompt=None):
    model = genai.GenerativeModel('gemini-1.5-flash')
    if image:
        response = model.generate_content([input_text, image[0], prompt])
    else:
        response = model.generate_content([input_text])
    return response.text

# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function for text-to-speech conversion
def text_to_speech(text, lang):
    language = "en" if lang == "English" else "ta"
    tts = gTTS(text=text, lang=language, slow=False)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    tts.save(temp_file.name)
    return temp_file.name

st.set_page_config(page_title="drug_pills_recognizer")

st.header("AI-Powered Smart Pill Recognition System")
with st.sidebar:
# Dropdown for choosing input method
    input_method = st.selectbox("Choose Input Method", ["Upload Image", "Scan Image"])

    # Reset session state if input method changes
    if input_method != st.session_state.previous_input_method:
        if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
            os.remove(st.session_state.audio_file_path)
        st.session_state.audio_file_path = None
        st.session_state.is_playing = False
        st.session_state.response = ""
        st.session_state.chat_history = []
        st.session_state.previous_input_method = input_method

    uploaded_file = None
    if input_method == "Upload Image":
        # File uploader for image upload
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "webp"])
        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image.", width=300)
        else:
            # Reset session state if image is deleted
            if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
                os.remove(st.session_state.audio_file_path)
            st.session_state.audio_file_path = None
            st.session_state.is_playing = False
            st.session_state.response = ""
            st.session_state.chat_history = []
    elif input_method == "Scan Image":
        uploaded_file = st.camera_input("Take a picture")

        if uploaded_file is not None:
            st.image(uploaded_file, caption="Captured Image.")
        else:
            # Reset session state if scanned image is cleared
            if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
                os.remove(st.session_state.audio_file_path)
            st.session_state.audio_file_path = None
            st.session_state.is_playing = False
            st.session_state.response = ""
            st.session_state.chat_history = []  
# Language selection in main content
language_options = ["English", "Tamil"]
selected_language = st.selectbox("Choose a language:", language_options, index=language_options.index("English"))

# Reset session state if language changes
if selected_language != st.session_state.previous_language:
    if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
        os.remove(st.session_state.audio_file_path)
    st.session_state.audio_file_path = None
    st.session_state.is_playing = False
    st.session_state.response = ""
    st.session_state.chat_history = []
    st.session_state.previous_language = selected_language

# Button to trigger processing
# Button to trigger processing
submit = st.button("Tell me about the medicine")

input_prompt = f"""
        You are an expert in identifying medicines and pills. You will be provided with images of medicines or pills. 
        Your task is to:
        1. Identify the name of the medicine (typically written in larger letters, often at the top or center of the packaging).
        2. Describe the medical conditions and problems the medicine cures and all the rerlevant information about the particular medicine.

        Reply strictly in {selected_language}. 

        If the image is unclear, incomplete, or does not contain a recognizable medicine, respond with: 
        "Recheck your medicine and upload."

        Avoid providing any irrelevant or generic responses, and do not suggest consulting a doctor or give unnecessary disclaimers.
        """


# If submit button is clicked
if submit:
    # Clear previous audio file if a new image or language change occurs
    if st.session_state.audio_file_path and os.path.exists(st.session_state.audio_file_path):
        os.remove(st.session_state.audio_file_path)
        st.session_state.audio_file_path = None

    if input_method == "Upload Image" and uploaded_file:
        # Setup image data
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, '')
        response=response.replace('*','')
        # Store the response in session state
        st.session_state.response = response

    elif input_method == "Scan Image" and uploaded_file:
        # Convert captured image to bytes for processing
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, '')
        response=response.replace('*','')
        # Store the response in session state
        st.session_state.response = response

    else:
        st.error("No image provided. Please upload or scan an image.")
        st.session_state.response = None

    if st.session_state.response:
        # Clean response for English by removing special characters
        if selected_language == 'English':
            st.session_state.response = re.sub(r'[^a-zA-Z0-9.\s]', '', st.session_state.response)

        # Generate audio file for response
        audio_file_path = text_to_speech(st.session_state.response, selected_language)
        st.session_state.audio_file_path = audio_file_path
        st.session_state.is_playing = True

# Always display the response if available
if st.session_state.response:
    st.markdown("<h3 style='color:seagreen;'>The Response is</h3>", unsafe_allow_html=True)
    st.write(st.session_state.response)


# Display audio player if audio file is available
if st.session_state.audio_file_path:
    # Generate the audio file's base64 encoding
    with open(st.session_state.audio_file_path, "rb") as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode()

    if audio_base64:
        # Embed custom CSS for styling
        st.markdown(
            """
            <style>
            .custom-audio-player {
                width: 400px; /* Set desired width */
                height: 100px; /* Increase height for better visibility */
                margin: 10px auto;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #f3f3f3; /* Optional background for better visibility */
                border: 1px solid #ccc; /* Optional border */
                border-radius: 8px;
                padding: 10px;
            }
            .custom-audio-player audio {
                width: 100%; /* Fill the container width */
                height: 70px; /* Set a larger height for better icon visibility */
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Display audio player with a container for custom styling
        audio_html = f"""
        <div class="custom-audio-player">
            <audio id="audio" controls autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        </div>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# Chatbot feature
if st.session_state.response:
    st.subheader("Chat with Gemini about the Medicine")
    
    # Input field for user questions
    if "my_text" not in st.session_state:
        st.session_state.my_text = ""

    def submit():
        # time.sleep(3)
        st.session_state.my_text = st.session_state.widget
        st.session_state.widget = ""

    st.text_input("Enter text here", key="widget", on_change=submit)

    user_input = st.session_state.my_text.strip()
    if input_method != st.session_state.previous_input_method or selected_language != st.session_state.previous_language:
        st.session_state.chat_history = []

    # Handle the "Send" button for chat
    if st.button("Send", key="chat_send") and user_input:
        # Append user input to chat history
        if user_input!='':
            st.session_state.chat_history.append({"user": user_input})

        # Generate chatbot response
        chat_prompt = f"""
        The medicine name and description is: {st.session_state.response}.
            If the question is not directly related to the provided medicine, respond with:  
            "This question is not relevant to the medicine. Please ask about the provided medicine."
            Now answer questions about this medicine. Question: {user_input}.  
            Reply in {selected_language}.

        """

        chat_response = get_gemini_response(chat_prompt)
        # Append Gemini's response to chat history
        st.session_state.chat_history.append({"gemini": chat_response})

    for message in st.session_state.chat_history:
        if "user" in message:
            st.write(f"<img src='https://img.icons8.com/?size=100&id=23309&format=png&color=000000' style='vertical-align:middle; margin-right: 10px; width: 25px; height: 25px;' />  {message['user']}", unsafe_allow_html=True)
        if "gemini" in message:
            st.write(f"<img src='https://img.icons8.com/?size=100&id=L3uh0mNuxBXw&format=png&color=000000' style='vertical-align:middle; margin-right: 10px; width: 25px; height: 25px;' /> <span style='color:seagreen;'> {message['gemini']} </span>", unsafe_allow_html=True)
    
    

