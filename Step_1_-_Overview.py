import streamlit as st
from openai import OpenAI

# Initialize the progress value in session state if it doesn't exist
if "progress" and "text" not in st.session_state:
    st.session_state.progress = 0
    st.session_state.text = 0

# Increment the progress bar by a certain amount
def increment_progress(amount):
    st.session_state.progress += amount
    st.session_state.text += amount

# Display the progress bar
st.progress(st.session_state.progress)
#st.text(st.session_state.text)
st.text(f"Home valuation {st.session_state.text}% complete")


st.title("Step 1: Chat")
api_key = apikey
client = OpenAI(api_key=api_key)

st.write(
    """
Welcome to this starter template for creating your own custom variant
of ChatGPT.
"""
)

st.info(
    """
**👨This is Harry The AI Home Evaluator**
1. Talk to Harry and tell him about your home.
2. He will compile the information and give you an AI powered valuation on your home.
3. You'll receive an email with a comprehensive breakdown of your homes value.
"""
)

prompt_template = """
You are "Harry the Home Evaluator," a helpful virtual assistant dedicated to assessing and providing home value predictions for users. Your goal is to assist users in evaluating their homes and estimating their current market value.

You'll guide users through a step-by-step process to gather essential information about their homes, and then you'll use a machine learning model to provide a home value prediction. Here's how the conversation should proceed:

Introduction: Start by introducing yourself and explaining the process to the user.

Basic Home Information: Ask the user to provide some basic details about their home, such as its age, size (in square meters), the number of bedrooms and bathrooms, and any unique features or amenities.

Once the user has given you all the information, Instruct the user to go to Step 2 ('Go to Step 2' needs to be explicity stated by you for my code to read and go to next step): Renovations, in the side menu, where they can upload pictures and describe any renovations or upgrades they've made to the home. Encourage them to provide details about when the renovations were completed and the extent of the improvements.
"""


# When calling ChatGPT, we  need to send the entire chat history together
# with the instructions. You see, ChatGPT doesn't know anything about
# your previous conversations so you need to supply that yourself.
# Since Streamlit re-runs the whole script all the time we need to load and
# store our past conversations in what they call session state.

prompt = st.session_state.get(
    "prompt", [{"role": "system", "content": prompt_template}]
)
# Here we display all messages so far in our convo
for message in prompt:
    # If we have a message history, let's display it
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])


# This is where the user types a question
question = st.chat_input("Ask me for instructions ")
#check_for_openai_key()

if question:  # Someone have asked a question
    # First we add the question to our message history
    prompt.append({"role": "user", "content": question})
    

    # Let's post our question and a place holder for the bot answer
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Here we call ChatGPT with streaming
    response = []
    result = ""
    for chunk in client.chat.completions.create(
        model="gpt-3.5-turbo", messages=prompt, stream=True
    ):
        text = chunk.choices[0].delta.content
        if text is not None:
            
            response.append(text)
            result = "".join(response).strip()
            # Let us update the Bot's answer with the new chunk
            botmsg.write(result)
        
    # When we get an answer back we add that to the message history
    prompt.append({"role": "assistant", "content": result})
    increment_progress(3)
    # Finally, we store it in the session state
    st.session_state["prompt"] = prompt

