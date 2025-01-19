# Synthetic Data Generation App using OpenRouter

Welcome to the **Synthetic Data Generation App**, a powerful tool for generating synthetic conversation datasets tailored for chatbot training. This app leverages OpenRouter's API to create natural and anthropomorphic conversations based on user-defined traits, subtraits, and topics.

## Features
- Generate conversations with traits and subtraits for specific topics.
- Select from multiple models available on OpenRouter.
- Export generated conversations as JSONL or CSV files.
- Securely handle API keys with password input fields.

## 🚀 Live App
You can try the app live here:  
👉 **[Synthetic Data Generation App](https://synthetic-data-generation-buildfastwithai.streamlit.app/)**  

## How to Use
1. **Enter your OpenRouter API Key** in the sidebar.
2. Choose a model from the available options.
3. Provide details such as:
   - Trait (e.g., Friendly, Empathetic)
   - Subtrait (e.g., Humorous, Supportive)
   - Topic for the conversation.
4. Select the number of conversations to generate (1 to 20).
5. Click the **Generate Conversation** button to generate synthetic conversations.
6. Review the generated conversations and download them as JSONL or CSV.

## Requirements
- An OpenRouter API key. You can get one from [OpenRouter](https://openrouter.ai).
- A stable internet connection to access the app.

## Models Supported
The app supports the following models:
- `google/gemini-2.0-flash-thinking-exp:free`
- `google/gemini-2.0-flash-exp:free`
- `microsoft/phi-3-mini-128k-instruct:free`
- `meta-llama/llama-3.2-11b-vision-instruct:free`

## Installation (Optional for Local Use)
To run the app locally:
1. Clone the repository:
   ```bash
   git clone https://github.com/Tejwant17/Synthetic_Data_Generation_App.git
   cd repository-name
   
