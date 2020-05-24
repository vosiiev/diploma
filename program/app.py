from flask import Flask, Response, render_template, request, redirect, \
                    session, url_for, escape, abort
app = Flask(__name__)

import sklearn.datasets as skd


# categories = [
#     'невинний',
#     'сирота',
#     'герой',
#     'наставник',
#     'мандрівник',
#     'коханець',
#     'бунтар',
#     'творець',
#     'правитель',
#     'чарівник',
#     'мудрець',
#     'блазень',
# ]

categories = [
    'герой',
    'наставник',
    'коханець',
    'правитель',
    'чарівник',
]

data_train = skd.load_files('/home/vosiiev/DW/program/datasets', categories=categories, encoding='utf-8')
data_test = skd.load_files('/home/vosiiev/DW/program/test', categories=categories, encoding='utf-8')

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/train')
def train():
    return render_template('train.html')


@app.route('/execute', methods=['GET', 'POST'])
def execute():
    if request.method == 'POST':
        text_clf = Pipeline([('vect', TfidfVectorizer()),
                             ('clf', MultinomialNB())
                            ])
        text_clf.fit(data_train.data, data_train.target)

        text = []
        with open('/home/vosiiev/DW/program/test/наставник/text_3.txt') as f:
            for line in f:
                text.append(line)
        predicted = text_clf.predict(text)
        return redirect(url_for('result'))
    else:
        return render_template('execute.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        return redirect(url_for('execute'))
    else:
        return render_template('result.html')


@app.route('/archetypes')
def archetypes():
    return render_template('archetypes.html')


if __name__ == '__main__':
    app.run(debug=True)
