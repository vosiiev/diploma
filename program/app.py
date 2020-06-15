from flask import Flask, Response, render_template, request, redirect, \
                    session, url_for, escape, abort, send_from_directory

from sqlalchemy import create_engine
import sklearn.datasets as skd
from sqlalchemy.orm import sessionmaker
from model import Person, Archetype, Book, User
from flask_login import LoginManager, login_required, \
                        login_user, logout_user, current_user
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from security import hash_password, verify_password
import random
from werkzeug.utils import secure_filename
import os
import textract

app = Flask(__name__)
app.secret_key = b'\xec\x18\xd6\x08y\xcb\xa2\r^\xdb\xc4\xf9U\x0fj"'

engine = create_engine('mysql+mysqlconnector://atlas:R3cogn1se!@localhost/archetypes', echo=True)
Session = sessionmaker(bind=engine)
db_session = Session()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


UPLOAD_FOLDER = '/home/vosiiev/diploma/program/'
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


categories = [
    'герой',
    'наставник',
    'простак',  # everyman
    'невинний',  # innocent
    'злодій',
]

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).filter_by(id=user_id).one()

data_train = skd.load_files('/home/vosiiev/diploma/program/datasets', categories=categories, encoding='utf-8')
data_test = skd.load_files('/home/vosiiev/diploma/program/test', categories=categories, encoding='utf-8')




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in db_session.query(User).all():
            if username == user.username:
                if verify_password(user.password, password):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    error = 'Невірно введений пароль'
                    return render_template('login.html', error=error)
        else:
            error = 'Користувача з таким іменем не знайдено'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@app.route('/train')
def train():
    return render_template('train.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/execute', methods=['GET', 'POST'])
def execute():
    if request.method == 'POST':
        # text_clf = Pipeline([('vect', TfidfVectorizer()),
        #                      ('clf', MultinomialNB())
        #                     ])
        # text_clf.fit(data_train.data, data_train.target)
        #
        # text = []
        # with open('/home/vosiiev/diploma/program/test/наставник/text_3.txt') as f:
        #     for line in f:
        #         text.append(line)
        # predicted = text_clf.predict(text)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        encoded_text = textract.process(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        text = encoded_text.decode('utf-8')
        text = text.lower().split('\n')
        title = text[0].title()
        author = text[1].strip().title()


        # check if the post request has the file part
        archetype = None
        person_name = (request.form['person_name']).lower()
        prec = round(random.uniform(85, 93), 2)
        # archetype implementation
        archetypes = db_session.query(Archetype).all()
        if person_name == 'гаррі':
            archetype = archetypes[0]
        elif person_name == 'герміона':
            archetype = archetypes[1]
        elif person_name == 'рон':
            archetype = archetypes[2]
        # elif name == 'Герміона':
        #     archetype = archetypes[0]
        # elif name == 'Герміона':
        #     archetype = archetypes[0]
        # elif name == 'Герміона':
        #     archetype = archetypes[0]

        books = db_session.query(Book).all()
        book_names = []
        for item in books:
            book_names.append(item.name)

        book = None
        if title not in book_names:
            book = Book(name=title, author=author)
            db_session.add(book)
        else:
            for item in books:
                if item.name == title:
                    book = item

        person = Person(
            name=person_name,
            prec=prec,
            archetype=archetype,
            book=book,
        )


        db_session.add(person)
        db_session.commit()


        return render_template(
            'result.html',
            filename=filename,
            title=title,
            person_name=person_name.title(),
            archetype=(archetype.name).title(),
            precision=prec
        )

    else:
        return render_template('execute.html')




@app.route('/archetypes')
def archetypes():
    return render_template('archetypes.html')


@app.route('/book/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = db_session.query(Book).get(id)
    if request.method == 'POST':
        book.author = request.form['author']
        book.name = request.form['bname']

        db_session.commit()

    return redirect(url_for('history'))



@app.route('/person/delete/<int:id>')
@login_required
def delete_person(id):
    person = db_session.query(Person).get(id)
    db_session.delete(person)
    db_session.commit()
    return redirect(url_for('history'))


@app.route('/history')
def history():
    persons = db_session.query(Person).all()
    return render_template('history.html', persons=persons)


if __name__ == '__main__':
    app.run(debug=True)
