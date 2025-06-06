# -*- coding: utf-8 -*-

!pip install transformers

import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import pandas as pd
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Attention
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

data_file = open('/content/lastv.json').read()
intents = json.loads(data_file)

qa_data=[]

for intent in intents['intents']:
    patterns = intent.get('patterns', [])
    responses = intent.get('responses', [])
    tag = intent.get('tag', "")

    for pattern in patterns:
        for response in responses:
            qa_data.append({'question': pattern, 'Tag': tag, 'answer': response})

df = pd.DataFrame(qa_data)
df

import re
def clean_text(text):
    text = text.lower()
    text = re.sub("https?://\S+|www\.\S+", "", text)
    text = " ".join(filter(lambda x: x[0] != "@", text.split()))

    return text

df.question = df.question.map(clean_text)
df.answer = df.answer.map(clean_text)

def add_start_end(text):
    text = f"<end> {text} <start> "
    return text

df.question = df.question.map(add_start_end)
df.answer = df.answer.map(add_start_end)
df

def tokenize(lang):
    lang_tokenizer = tf.keras.preprocessing.text.Tokenizer(
        oov_token="<OOV>", filters='!"#$%&()*+,-./:;=?@[\\]^_`{|}~\t\n'
    )
    lang_tokenizer.fit_on_texts(lang)
    tensor = lang_tokenizer.texts_to_sequences(lang)
    tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, padding="post")
    return tensor, lang_tokenizer

question_tensor, question_tokenizer = tokenize(df.question)
answer_tensor, answer_tokenizer = tokenize(df.answer)

x_train, x_test, y_train, y_test = train_test_split(question_tensor, answer_tensor, test_size=0.2, random_state=42)

max_encoder_sequence_length = 10
max_decoder_sequence_length = 58
vocab_inp_size = len(question_tokenizer.word_index) + 1
vocab_tar_size = len(answer_tokenizer.word_index) + 1

embedding_dim = 128
units = 256
batch_size = 5
epochs = 50

x_train.shape, y_train.shape, x_test.shape, y_test.shape

x_train

def convert(token, tensor):
    for t in tensor:
        if t != 0:
            print("%d ----> %s" % (t, token.index_word[t]))

print("question ; index to word mapping")
convert(question_tokenizer, x_train[0])
print()
print("answar; index to word mapping")
convert(answer_tokenizer, y_train[0])

# @title Default title text
def create_data_pipline(x, y, batch_size=32):
    data = tf.data.Dataset.from_tensor_slices((x, y))
    data = data.shuffle(1028)
    data = data.batch(batch_size, drop_remainder=True)
    data = data.prefetch(tf.data.AUTOTUNE)
    return data

train_dataset = create_data_pipline(x_train, y_train)
test_dataset = create_data_pipline(x_test, y_test)

# @title Default title text
for question, answer in train_dataset.take(1):
    print(f"question:{question.shape}\n{question}")

    print(f"answer:{answer.shape}\n{answer}")
    question_sample = question
    answer_sample = answer

encoder_input = Input(shape=(max_encoder_sequence_length,))
encoder_embedding = Embedding(input_dim=vocab_inp_size, output_dim=embedding_dim)(encoder_input)
encoder_lstm = LSTM(units=units, return_state=True)
encoder_output, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_input = Input(shape=(max_decoder_sequence_length,))
decoder_embedding = Embedding(input_dim=vocab_tar_size, output_dim=embedding_dim)(decoder_input)
decoder_lstm = LSTM(units=units, return_sequences=True, return_state=True)
decoder_output, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)

output_dense = Dense(vocab_tar_size, activation='softmax')
output = output_dense(decoder_output)

AI_DOJO_chatbot_model = Model(inputs=[encoder_input, decoder_input], outputs=output)

# Use Adam optimizer with a customizable learning rate
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

AI_DOJO_chatbot_model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
tf.keras.utils.plot_model(AI_DOJO_chatbot_model, to_file='chatbot_model.png', show_shapes=True)

AI_DOJO_chatbot_model.summary()

from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical

y_train_onehot = [to_categorical(sequence, num_classes=vocab_tar_size) for sequence in y_train]
y_train_onehot = pad_sequences(y_train_onehot, padding='post', maxlen=max_decoder_sequence_length)

history = AI_DOJO_chatbot_model.fit(
    x=[x_train, y_train],
    y=y_train_onehot,
    batch_size=batch_size,
    epochs=22,
    validation_split=0.1
)

AI_DOJO_chatbot_model.save('AI_DOJO.h5')

from tensorflow.keras.models import load_model

model = load_model('AI_DOJO.h5')

"""# Task
Create a command-line interface for the chatbot code provided in the previous turn, allowing for interactive input and output.

## Load the saved model

### Subtask:
Load the chatbot model that was saved in the previous step.

**Reasoning**:
Load the saved Keras model using the `load_model` function.
"""

from tensorflow.keras.models import load_model

model = load_model('AI_DOJO.h5')

"""## Create prediction function

### Subtask:
Define a function that takes user input, preprocesses it, uses the model to predict a response, and post-processes the output.

**Reasoning**:
Define the predict_response function to handle user input, preprocess it, use the model for prediction, and postprocess the output.
"""

# Create a separate encoder model for inference
encoder_inputs_inf = Input(shape=(max_encoder_sequence_length,), name='encoder_inputs_inf')
encoder_embedding_inf = Embedding(input_dim=vocab_inp_size, output_dim=embedding_dim)(encoder_inputs_inf)
encoder_lstm_inf = LSTM(units=units, return_state=True)
encoder_output_inf, state_h_inf, state_c_inf = encoder_lstm_inf(encoder_embedding_inf)
encoder_states_inf = [state_h_inf, state_c_inf]
encoder_model = Model(inputs=encoder_inputs_inf, outputs=encoder_states_inf)


# Create a separate decoder model for inference
decoder_inputs_inf = Input(shape=(1,), name='decoder_inputs_inf')
decoder_state_h_input_inf = Input(shape=(units,), name='decoder_state_h_input_inf')
decoder_state_c_input_inf = Input(shape=(units,), name='decoder_state_c_input_inf')
decoder_states_inputs_inf = [decoder_state_h_input_inf, decoder_state_c_input_inf]

decoder_embedding_inf = Embedding(input_dim=vocab_tar_size, output_dim=embedding_dim)(decoder_inputs_inf)
decoder_lstm_inf = LSTM(units=units, return_sequences=True, return_state=True)
decoder_outputs_inf, state_h_inf, state_c_inf = decoder_lstm_inf(decoder_embedding_inf, initial_state=decoder_states_inputs_inf)
output_dense_inf = Dense(vocab_tar_size, activation='softmax')
decoder_outputs_inf = output_dense_inf(decoder_outputs_inf)
decoder_states_inf = [state_h_inf, state_c_inf]
decoder_model = Model([decoder_inputs_inf] + decoder_states_inputs_inf, [decoder_outputs_inf] + decoder_states_inf)


def predict_response(user_input):
    # Preprocess user input
    cleaned_input = clean_text(user_input)
    preprocessed_input = add_start_end(cleaned_input)

    # Tokenize and pad user input
    input_sequence = question_tokenizer.texts_to_sequences([preprocessed_input])
    encoder_input_data = pad_sequences(input_sequence, maxlen=max_encoder_sequence_length, padding="post")

    # Get the initial state from the encoder
    states_value = encoder_model.predict(encoder_input_data)

    # Create initial decoder input (start token)
    start_token_index = answer_tokenizer.word_index['<end>']
    target_sequence = np.zeros((1, 1), dtype='int32')
    target_sequence[0, 0] = start_token_index


    # Predict output sequence token by token
    response_words = []
    for _ in range(max_decoder_sequence_length):
        output_tokens, h, c = decoder_model.predict([target_sequence] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_word = answer_tokenizer.index_word.get(sampled_token_index, '')

        # Exit condition: either hit max length or find stop token.
        if sampled_word == '<start>':
            break

        # Append token
        if sampled_word != '<end>':
             response_words.append(sampled_word)

        # Update the target sequence (of length 1).
        target_sequence = np.zeros((1, 1), dtype='int32')
        target_sequence[0, 0] = sampled_token_index

        # Update states
        states_value = [h, c]

    response = " ".join(response_words)

    return response

"""## Implement interactive loop

### Subtask:
Create a loop that prompts the user for input, calls the prediction function, and prints the chatbot's response.

**Reasoning**:
Start an infinite loop to handle user input and generate responses.
"""

while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
    response = predict_response(user_input)
    print(f"Chatbot: {response}")
