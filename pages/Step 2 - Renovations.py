import streamlit as st
import base64
#import databutton as db

from openai import OpenAI

# Retrieve the chat history from the previous page
previous_chat_history = st.session_state.get("prompt")

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


st.set_page_config(
    page_title="Renovations", layout="centered", initial_sidebar_state="collapsed"
)
# Streamlit page setup
st.title("Step 2: Renovations")


# Retrieve the OpenAI API Key from secrets
api_key = apikey

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("Image", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

# Toggle for showing additional details input
additional_details = st.text_area(
    "Add any additional details or context about the image here:",
)

# Button to trigger the analysis
analyze_button = st.button("Upload Images", type="secondary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:
    with st.spinner("Analysing the image ..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)

        # Create the prompt text with the previous chat history as context
        prompt_text = "You are Harry the Home Evaluator, a helpful virtual assistant dedicated to assessing and providing home value predictions for users. Your goal is to assist users in evaluating their homes and estimating their current market value. "
        if previous_chat_history:
            prompt_text += "Previously, you had a conversation with the user:\n"

            for message in previous_chat_history:
                if message["role"] == "user":
                    prompt_text += f"- User: {message['content']}\n"
                elif message["role"] == "assistant":
                    prompt_text += f"- Assistant: {message['content']}\n"

        prompt_text += (
            "You are now to receive images of any renovations the user has made, along with a description of those renovations. "
            "You must comment on the renovations, make observations on what was done, and compliment the user for doing a good job."
            "You must then instruct the user to go to the next page to receive their final valuation "
        )
        
        if additional_details:
            prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"

        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            }
        ]

        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1200,
                stream=True,
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")

else:
    # Warnings for user action required
    if not uploaded_file and additional_details and analyze_button:
        prompt_text = "You are Harry the Home Evaluator, a helpful virtual assistant dedicated to assessing and providing home value predictions for users. Your goal is to assist users in evaluating their homes and estimating their current market value. "
        if previous_chat_history:
            prompt_text += "Previously, you had a conversation with the user:\n"

            for message in previous_chat_history:
                if message["role"] == "user":
                    prompt_text += f"- User: {message['content']}\n"
                elif message["role"] == "assistant":
                    prompt_text += f"- Assistant: {message['content']}\n"

        prompt_text += (
            "You are now to recieve details on the customers renovations, but you were not uploaded an image. please recommend the customer upload an image for a more accurate valuation "
            "You must comment on the renovations, make observations on what was done, and compliment the user for doing a good job."
            "You must then instruct the user to go to the next page to receive their final valuation "
        )
        

        prompt_text += f"\n\nAdditional Context Provided by the User:\n{additional_details}"

        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    
                ],
            }
        ]
        #st.warning("Please upload an image.")
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1200,
                stream=True,
            ):
                # Check if there is content to display
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            # Final update to placeholder after the stream ends
            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    if not api_key:
        st.warning("Please enter your OpenAI API key.")

st.write(previous_chat_history)
