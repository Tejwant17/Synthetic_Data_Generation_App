import streamlit as st
import pandas as pd
import json
import requests
import re

st.title("Synthetic Data Generation App using OpenRouter")
st.sidebar.header("Configuration")

api_key = st.sidebar.text_input("Enter OpenRouter API Key", type="password",
                                help="Your OpenRouter API key. Keep it secure!")


def validate_api_key(key):
    test_url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {key}"}
    try:
        response = requests.get(test_url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


if api_key and not validate_api_key(api_key):
    st.sidebar.error("Invalid API Key. Please enter a valid key.")

# Track model changes with session state
if 'last_model' not in st.session_state:
    st.session_state.last_model = None
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

model = st.sidebar.selectbox(
    "Choose a Model",
    ["google/gemini-2.0-flash-thinking-exp:free",
     "google/gemini-2.0-flash-exp:free",
     "microsoft/phi-3-mini-128k-instruct:free",
     "meta-llama/llama-3.2-11b-vision-instruct:free"
     ],
    help="Select a model to generate the synthetic conversations."
)

# Reset conversations when the model changes
if model != st.session_state.last_model:
    st.session_state.conversations = []
    st.session_state.last_model = model

if st.sidebar.button("Reset Conversations"):
    st.session_state.conversations = []

# Trait and Subtrait Inputs
trait = st.sidebar.text_input("Enter a Trait", help="A general characteristic (e.g., Friendly, Empathetic).")
subtrait = st.sidebar.text_input("Enter a Subtrait",
                                 help="A specific aspect of the trait (e.g., Humorous, Supportive).")

# Topic Input
topic = st.sidebar.text_input(
    "Enter the Topic for Conversation",
    value="General",
    help="The main topic for the conversation (Default: General)."
)

# Number of Conversations
num_conversations = st.sidebar.slider(
    "Number of Conversations",
    min_value=1,
    max_value=20,
    value=10,
    help="Select the number of conversations to generate."
)

log_placeholder = st.empty()


# Function to fetch synthetic conversation
def generate_human_data(trait, subtrait, api_key, topic="General", num=10):
    # Prompt construction
    prompt = f"""
    Create {num} examples for instruct dataset for training chatbots to be more anthropomorphic.
    Following the below instructions:
    1. Use natural language with emojis and show emotions.
    2. Focus on the conversation conforming to:
       - Trait: {trait}
       - Subtrait: {subtrait}
    3. The topic of the conversation should be: {topic}.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": """Generate a list of conversations between a user and a bot in the following JSON format:
                    {
                        "conversations": [
                            {"user": "User's message here", "bot": "Bot's response here"}
                        ]
                    }"""
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 1,
        "top_p": 1,
        "top_k": 0,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "repetition_penalty": 1,
        "min_p": 0,
        "top_a": 0,
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()

        # Debug raw response
        raw_response = response.text
        print("Raw response:", raw_response)

        # Handle non-JSON responses
        cleaned_content = response.text.strip()

        try:
            data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if match:
                valid_json = match.group(0)
                data = json.loads(valid_json)
            else:
                st.error("No valid JSON found in the response.")
                return None

        # Validate response structure
        if not isinstance(data, dict) or "choices" not in data or not data["choices"]:
            st.error("Unexpected API response structure.")
            return None

        conversation_content = data["choices"][0].get("message", {}).get("content", None)
        if conversation_content is None:
            st.error("The response did not contain conversation data.")
            return None

        conversations = []
        # Find all conversation blocks using regex
        examples = re.findall(r'\{\s*"conversations":\s*\[.*?\]\s*\}', conversation_content, re.DOTALL)

        for example in examples:
            try:
                # Parse each conversation example and extract user-bot pairs
                conversation_json = json.loads(example)
                for conv in conversation_json.get("conversations", []):
                    conversations.append({"User": conv["user"], "Bot": conv["bot"]})
            except json.JSONDecodeError as e:
                st.warning(f"Skipping invalid conversation example: {e}")
                continue

        if not conversations:
            st.error("No valid conversations generated.")
            return None

        return conversations

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None


# Button to generate conversations
if st.sidebar.button("Generate Conversation"):
    if api_key and trait and subtrait:
        st.info("Generating conversations... Please wait.")
        result = generate_human_data(trait, subtrait, api_key, topic, num_conversations)

        if result:
            st.write("Generated Conversations")
            conversation_list = []
            for idx, conv in enumerate(result):
                conversation_list.append(
                    f"**Conversation {idx + 1}:**\n\n"
                    f"**User:** {conv['User']}\n\n"
                    f"**Bot:** {conv['Bot']}\n"
                )
            st.markdown("\n\n".join(conversation_list))

            # Format for download options
            jsonl_data = "\n".join(
                json.dumps({
                    "messages": [
                        {'role': 'system', 'content': "You are a friendly assistant."},
                        {"role": "user", "content": conv["User"]},
                        {"role": "assistant", "content": conv["Bot"]}
                    ]
                }) for conv in result
            )
            st.download_button(
                label="Download as JSONL",
                data=jsonl_data,
                file_name="conversations.jsonl",
                mime="application/jsonl",
            )
            csv_data = "\n".join([f'{conv["User"]}, {conv["Bot"]}' for conv in result])
            st.download_button(
                label="Download as CSV",
                data=f"User, Bot\n{csv_data}".encode("utf-8"),
                file_name="conversations.csv",
                mime="text/csv"
            )
        else:
            st.write("No conversations generated.")

# Footer
st.markdown("---")
st.markdown("Made by Tejwant Singh @BuildFastwithai")