from aitextgen import aitextgen
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import flask
import numpy as np
import pickle

# start flask app
app = flask.Flask(__name__, template_folder='templates')

# function to reweight distribution using temperature sampling for LSTM
def sample(prediction, temperature):
    prediction = np.asarray(prediction).astype('float64')
    prediction = np.log(prediction) / temperature
    prediction_exp = np.exp(prediction)
    prediction = prediction_exp / np.sum(prediction_exp)
    probabilities = np.random.multinomial(1, prediction, 1)
    return np.argmax(probabilities)

# function to predict lyrics for LSTM
def predict_lyrics(seed, n):
    line_count = 0
    seed = 'starttag ' + seed

    while True:
        tokens = tokenizer.texts_to_sequences([seed])[0]
        tokens = pad_sequences([tokens], maxlen=max_seq_len-1, padding='pre')

        prediction = lstm.predict(tokens, verbose=0)
        predicted_index = sample(prediction[0], 1.2)

        predicted_word = ''
        for word, index in tokenizer.word_index.items():
            if predicted_index == index:
                predicted_word = word
                break
        if predicted_word == 'endtag':
            line_count += 1

        if line_count == n:
            return seed
        else:
            seed += ' ' + predicted_word

# function to generate lyrics using LSTM
def lstm_generate_lyrics(seed, n):
    lyrics = predict_lyrics(seed, n)
    lyrics = lyrics.split('endtag')

    for i in range(len(lyrics)):
        line = lyrics[i]
        words = line.split()
        if 'starttag' in words:
            words.remove('starttag')
        line = ' '.join(words)
        lyrics[i] = line

    return lyrics

# function to generate lyrics using transformer
def transformer_generate_lyrics(seed, n):
    lyrics = transformer.generate_one(prompt=seed, max_length=512, top_k=50, top_p=0.9, repetition_penalty=1.5)
    lyrics = lyrics.split('\n')[0:n]
    return lyrics

# set up index page
@app.route('/', methods=['GET', 'POST'])
def main():
    # declare global variables for LSTM, transformer
    global lstm, tokenizer, max_seq_len, transformer

    # if HTTP GET request
    if flask.request.method == 'GET':
        # return page with form
        return(flask.render_template('index.html'))

    # if HTTP POST request
    if flask.request.method == 'POST':
        # get input from form
        dataset = flask.request.form['dataset']
        model = flask.request.form['model']
        seed = flask.request.form['seed']
        n = flask.request.form['n']

        # if selected dataset is Lou Reed
        if str(dataset) == 'loureed':
            # if selected model is LSTM
            if str(model) == 'lstm':
                # load model, load tokenizer, set max sequence length
                lstm = load_model('models/lstm1/lstm.h5')
                tokenizer = pickle.load(open('models/lstm1/tokenizer.pkl', 'rb'))
                max_seq_len = 60
                # generate lyrics
                lyrics = lstm_generate_lyrics(str(seed), int(n))
            # if selected model is transformer
            if str(model) == 'transformer':
                # load transformer
                transformer = aitextgen(model='models/transformer1/transformer.bin', config='models/transformer1/config.json')
                # generate lyrics
                lyrics = transformer_generate_lyrics(str(seed), int(n))

        # if selected dataset is punk
        if str(dataset) == 'punk':
            # if selected model is LSTM
            if str(model) == 'lstm':
                # load model, load tokenizer, set max sequence length
                lstm = load_model('models/lstm2/lstm.h5')
                tokenizer = pickle.load(open('models/lstm2/tokenizer.pkl', 'rb'))
                max_seq_len = 46
                # generate lyrics
                lyrics = lstm_generate_lyrics(str(seed), int(n))
            # if selected model is transformer
            if str(model) == 'transformer':
                transformer = aitextgen(model='models/transformer2/transformer.bin', config='models/transformer2/config.json')
                # generate lyrics
                lyrics = transformer_generate_lyrics(str(seed), int(n))

        # return page with form, generated lyrics
        return flask.render_template('index.html', dataset=dataset, model=model, seed=seed, n=n, lyrics=lyrics)

if __name__ == '__main__':
    # run app on local server
    app.run()
