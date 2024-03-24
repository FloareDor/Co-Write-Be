import pandas as pd

message=pd.read_csv("machine_data/dataset.csv")

import re
import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()
corpus = []
for i in range(0, len(message)):
    review = re.sub('[^a-zA-Z]', ' ', message['prompt'][i])
    review = review.lower()
    review = review.split()

    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)
    corpus.append(review)

from sklearn.feature_extraction.text import CountVectorizer

cv = CountVectorizer(max_features=100)
X = cv.fit_transform(corpus).toarray()

y=pd.get_dummies(message['label'])
y=y.iloc[:,1].values



corpus = []
for i in range(0, len(message)):
    review = re.sub('[^a-zA-Z]', ' ', message['prompt'][i])
    review = review.lower()
    review = review.split()

    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)
    corpus.append(review)
from joblib import load
# Load the saved model from the file
spam_detect_model = load('machine_data/spam_detection_model.joblib')
def predict_sentence(query, vectorizer, classifier):
    # Preprocess the input sentence
    review = re.sub('[^a-zA-Z]', ' ', query)
    review = review.lower()
    review = review.split()
    review = [ps.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)

    # Fit the CountVectorizer on the training data if not already fitted
    if not hasattr(vectorizer, 'vocabulary_'):
        vectorizer.fit(corpus)  # Assuming 'corpus' is your preprocessed text data

    # Transform the preprocessed sentence into a numerical feature vector
    sentence_vector = vectorizer.transform([review]).toarray()

    # Use the trained classifier to predict the label for the preprocessed sentence
    predicted_label = classifier.predict(sentence_vector)
    return predicted_label[0]


query = "Complete"  # Replace with your sample text
predicted_label = predict_sentence(query, cv, spam_detect_model)
print("Predicted Label:", predicted_label)