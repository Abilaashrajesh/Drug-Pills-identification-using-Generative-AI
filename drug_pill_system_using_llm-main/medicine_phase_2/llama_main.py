import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

# Initialize Groq client
client = Groq(api_key="GROQ API KEY")
llava_model = 'llama-3.2-11b-vision-preview'

# Function to encode image to base64
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
    

# Function to get text from image using Groq API
def image_text(client, model, base64_image, prompt):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "You are a helpful assistant who helps in extract name from image."},
                {
                    "type": 'image_url',
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        },
        {
            "role":"user",
            "content":prompt
        }
    ]
    chat_completion = client.chat.completions.create(messages=messages, model=model)
    return chat_completion.choices[0].message.content

# Streamlit UI
st.title("Medicine Identification App")
st.write("Upload an image of a medicine or pill..")

# Image upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image',width=300)
    submit = st.button("Tell me about the image")
    if submit:
        if image:
        # Encode image to base64
            base64_image = encode_image(image)

            # Define the prompt
            prompt = """ You are given an image, 
            your task is to extract name of the medicine and the use of the medicine.
            if the given image is not  a medicine reply 'Recheck your medicine and upload a clear image'."""

            # Get the response from the model
            with st.spinner('Analyzing the image...'):
                response = image_text(client, llava_model, base64_image, prompt)

            # Display the response
            st.subheader("Response")
            st.write(response)
        else:
            st.error("No image Provided please upload a medicine image.")
