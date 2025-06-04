
from flask import Flask, render_template, request, jsonify
import random
import time
import numpy as np
import pickle
import json
from keras.models import load_model
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

model = load_model('chatbot_model.h5')
data = pickle.load(open('intent_data.pkl', 'rb'))  
words = data['words']
classes = data['classes']

app = Flask(__name__)

with open('lastv.json', 'r', encoding='utf-8') as json_file:
    data_file = json_file.read()
intents = json.loads(data_file)

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)  
    bag = [1 if w in sentence_words else 0 for w in words]
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]

    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)

    return_list = [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]
    return return_list

def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    for intent in list_of_intents:
        if intent['tag'] == tag:
            result = random.choice(intent['responses'])
            break
    return result

def chatbot_response(text, model, intents_json):
    ints = predict_class(text, model)
    res = get_response(ints, intents_json)
    return res

def respond(message, chat_history):
    try:
        bot_message = chatbot_response(message, model, intents)
        chat_history.append((message, bot_message))
        time.sleep(1)
    except Exception as e:
        print("An error occurred:", e)
    return "", chat_history

chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    response = respond(user_message)
    return jsonify(response)

def respond(message):
    try:
        bot_message = chatbot_response(message, model, intents)
        chat_history.append((message, bot_message))
        time.sleep(1)
    except Exception as e:
        print("An error occurred:", e)
    return {"bot_message": bot_message, "chat_history": chat_history}

if __name__ == '__main__':
    app.run(debug=True)