# -*- coding: utf-8 -*-
"""lstm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fUJUXaFnE0X1eVOzy4q-yfW5EKZI-7PH
"""

!nvidia-smi -L

from nltk.translate.bleu_score import corpus_bleu
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.layers import Bidirectional, Dense, Dropout, Embedding, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import plot_model, to_categorical
import matplotlib.pyplot as plt
import numpy as np
import pickle
import re

"""## Preparing the data"""

# read dataset from text file
with open('dataset1.txt', 'r') as file:
  dataset_str = file.read()

# remove apostrophes
dataset_str = re.sub('\'', '', dataset_str)

# replace punctuation with single whitespace
dataset_str = re.sub(r'[^\w\s]', ' ', dataset_str)

# replace multiple whitespace with single whitespace
dataset_str = re.sub(' +', ' ', dataset_str)

# convert to lowercase
dataset_str = dataset_str.lower()

# split dataset into lines
dataset_lst = dataset_str.split('\n')

# get rid of empty lines in dataset
dataset_lst = [line for line in dataset_lst if line.strip() != '']

# get rid of duplicate lines in dataset
dataset_lst = list(dict.fromkeys(dataset_lst))

# add start and end tags to every line
dataset1 = []
for i in range(len(dataset_lst)):
  line = 'starttag ' + dataset_lst[i] + ' endtag'
  dataset1.append(line)

# augment dataset by combining lines 
dataset2 = []
for i in range(len(dataset1)):
  if i+1 in range(len(dataset1)):
    line = dataset1[i] + ' ' + dataset1[i+1]
    dataset2.append(line)

# combine datasets
dataset = dataset1 + dataset2

"""## Building the model"""

# fit tokenizer on dataset to convert words into numbers
tokenizer = Tokenizer()
tokenizer.fit_on_texts(dataset)

# vocabulary size is tokenizer length + 1, for a new unknown word
vocab_size = len(tokenizer.word_index) + 1

# initialise sequences
seqs = []

# for each line in dataset
for i in range(len(dataset)):
  # convert line to vector
  tokens = tokenizer.texts_to_sequences([dataset[i]])[0]
  # for each word in line
  for i in range(1, len(tokens)):
    # prepare sequence
    seq = tokens[:i+1]
    # append to sequences
    seqs.append(seq)

# find length of longest sequence
max_seq_len = max([len(seq) for seq in seqs])

# prepad sequences to max sequence length
seqs = np.array(pad_sequences(seqs, maxlen=max_seq_len, padding='pre'))

# prepare features, label
features, label = seqs[:,:-1], seqs[:,-1]

# one-hot encode the label
label = to_categorical(label, num_classes=vocab_size)

# build model
model = Sequential()
model.add(Embedding(vocab_size, 50, input_length=max_seq_len-1))
model.add(Bidirectional(LSTM(150, return_sequences=True)))
model.add(Dropout(0.2))
model.add(LSTM(100))
model.add(Dense(vocab_size/2, activation='relu'))
model.add(Dense(vocab_size, activation='softmax'))

# compile model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics='accuracy')

# summarise model
model.summary()

# visualise model
plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True, dpi=100)

# train model for 100 epochs
history = model.fit(features, label, epochs=100, verbose=1)

# evaluate model after training
results = model.evaluate(features, label, verbose=1)

"""## Evaluating the model"""

# function to reweight distribution using temperature sampling
def sample(prediction, temperature):
  prediction = np.asarray(prediction).astype('float64')
  prediction = np.log(prediction) / temperature
  prediction_exp = np.exp(prediction)
  prediction = prediction_exp / np.sum(prediction_exp)
  probabilities = np.random.multinomial(1, prediction, 1)
  return np.argmax(probabilities)

# function to predict lyrics
def predict_lyrics(seed, n):
  # initialise line count
  line_count = 0
  # add start tag to seed
  seed = 'starttag ' + seed

  # generate lyrics in a loop
  while True:
    # convert seed to vector
    tokens = tokenizer.texts_to_sequences([seed])[0]
    # prepad seed vector to max sequence length
    tokens = pad_sequences([tokens], maxlen=max_seq_len-1, padding='pre')

    # get prediction distribution for given input
    prediction = model.predict(tokens, verbose=0)
    # get predicted index
    predicted_index = sample(prediction[0], 1.2)

    # initialise predicted word
    predicted_word = ''
    # find predicted word using predicted index and tokenizer
    for word, index in tokenizer.word_index.items():
      if predicted_index == index:
        predicted_word = word
        break
    # if predicted word is an endtag, increment line count 
    if predicted_word == 'endtag':
      line_count += 1
    
    # if desired line count reached, return lyrics
    if line_count == n:
      return seed
    # else append predicted word
    else:    
      seed += ' ' + predicted_word

# function to generate lyrics
def generate_lyrics(seed, n):
  # get lyrics
  lyrics = predict_lyrics(seed, n)
  # split lyrics by end tags
  lyrics = lyrics.split('endtag')

  # for each line in lyrics
  for i in range(len(lyrics)):
    line = lyrics[i]
    # split line into words
    words = line.split()
    # remove start tag
    if 'starttag' in words:
      words.remove('starttag')
    # reconstruct line
    line = ' '.join(words)
    lyrics[i] = line

  # return lyrics
  return lyrics

# generate lyrics
lyrics = generate_lyrics('', 10)

# print lyrics
for i in range(len(lyrics)):
  print(lyrics[i])

# save model
model.save('lstm.h5')

# save tokenizer
pickle.dump(tokenizer, open('tokenizer.pkl', 'wb'))

# function to plot graph for metric against epoch
def plot_graph(history, metric):
  plt.plot(history.history[metric])
  plt.title('lstm - dataset1')
  plt.xlabel('epoch')
  plt.ylabel(metric)
  plt.savefig(metric + '.png', dpi=100)
  plt.show()

# plot graph for accuracy
plot_graph(history,'accuracy')

# plot graph for loss
plot_graph(history,'loss')

# store BLEU scores
bleu_scores = []

# run trial 100 times
for i in range(100):
  # candidate sentences are generated lyrics
  candidates = generate_lyrics('', 10)

  # split candidate sentences into words
  for i in range(len(candidates)):
    line = candidates[i].split()
    candidates[i] = line
  
  # reference sentences are dataset lyrics
  references = []
  for i in range(len(candidates)):
    references.append(dataset_lst)
  
  # calculate BLEU score
  bleu_score = corpus_bleu(references, candidates)

  # append to BLEU scores
  bleu_scores.append(bleu_score)

# print average BLEU score
print('BLEU: ', np.average(bleu_scores))

# store similarity scores
similarity_scores = []

# run trial 100 times
for i in range(100):
  # generate lyrics to compare to dataset
  lyrics = generate_lyrics('', 10)
  
  # for dataset, learn tf-idf and transform to document matrix
  tfidf_dataset = TfidfVectorizer().fit_transform(dataset_lst)
  
  # learn tf-idf for dataset
  tfidf_lyrics = TfidfVectorizer().fit(dataset_lst)
  # transform to document matrix for generated lyrics
  tfidf_lyrics = tfidf_lyrics.transform(lyrics)
  
  # calculate cosine similarities between dataset, generated lyrics
  similarities = cosine_similarity(tfidf_dataset, tfidf_lyrics).flatten()
  
  # find max similarity
  max_similarity = np.amax(similarities)

  # append to similarity scores
  similarity_scores.append(max_similarity)

# print average similarity score
print('Similarity: ', np.average(similarity_scores))