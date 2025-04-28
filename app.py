from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'hw13.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    students = query_db('SELECT * FROM students')
    quizzes = query_db('SELECT * FROM quizzes')
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        execute_db('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        execute_db('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)', (subject, num_questions, quiz_date))
        return redirect(url_for('dashboard'))
    return render_template('add_quiz.html')

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    students = query_db('SELECT * FROM students')
    quizzes = query_db('SELECT * FROM quizzes')
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        execute_db('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)', (student_id, quiz_id, score))
        return redirect(url_for('dashboard'))
    return render_template('add_result.html', students=students, quizzes=quizzes)

@app.route('/student/<int:student_id>')
def view_results(student_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    student = query_db('SELECT * FROM students WHERE id = ?', [student_id], one=True)
    results = query_db('''
        SELECT quizzes.subject, quizzes.quiz_date, results.score
        FROM results
        JOIN quizzes ON quizzes.id = results.quiz_id
        WHERE results.student_id = ?
    ''', [student_id])
    return render_template('view_results.html', student=student, results=results)

if __name__ == '__main__':
    app.run(debug=True)
