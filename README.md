This is an older version of the code. I plan to improve and refactor it when I have more time to work on it.

The current setup is built for Arabic, with simple responses stored in a JSON file. You can open the file to see how it's structured. If you’d like to adapt it for English, you can simply modify or replace the JSON file with English responses.

As for the model_code.py file — it’s not required to run the chatbot. It’s included for those who are curious about how the model was trained or want to understand the architecture behind it.
for the website:
# Chatbot Web App

This is a web-based chatbot application built with Flask, Keras, and jQuery. The chatbot uses a trained neural network model to understand user input and respond accordingly. The interface allows users to chat with the bot and view product information.

## Features

- Interactive chatbot with natural language understanding
- Product showcase with images and specifications
- Responsive web interface with chat window
- Supports both English and Arabic queries

## Project Structure

- `app.py`: Main Flask application
- `chatbot_model.h5`: Trained Keras model for intent classification
- `intent_data.pkl`: Preprocessed data for the model
- `lastv.json`: Intents and responses in JSON format
- `static/`: Static files (CSS, JS, images)
- `templates/index.html`: Main web page

## How to Run

1. Install requirements:
    ```sh
    pip install flask keras nltk numpy
    ```
2. Download NLTK data (if not already):
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('wordnet')
    ```
3. Start the Flask app:
    ```sh
    python app.py
    ```
4. Open your browser and go to `http://127.0.0.1:5000/`

## Usage

- Type your message in the chat window and press send.
- The chatbot will respond based on the trained intents.


# the model_code.py:

## Introduction

This project implements a simple chatbot using a Sequence-to-Sequence model with LSTM layers. The chatbot is designed to answer questions based on a custom dataset of question-answer pairs.

The core technologies used in this project include:

-   **TensorFlow/Keras**: For building and training the deep learning model.
-   **LSTM (Long Short-Term Memory)**: The type of recurrent neural network layer used in the Sequence-to-Sequence architecture to handle sequential data.
-   **NLTK**: For natural language processing tasks like tokenization.
-   **Pandas**: For data manipulation and preparation.

## Credits

Developed by Mustafa Mahmoud Kareem.
