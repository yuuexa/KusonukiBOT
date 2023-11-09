from flask import render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy import desc
from KusonukiBOT import app, db
from KusonukiBOT.models.user import User
from KusonukiBOT.models.assignment import Assignment
from KusonukiBOT.models.timetable import Timetable
from KusonukiBOT.models.examination import Examination
from KusonukiBOT.models.quiz import Quiz
from KusonukiBOT.models.message import Message
import datetime
import platform

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

weekday = ['月', '火', '水', '木', '金', '月', '月']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    day = datetime.datetime.today() + datetime.timedelta(days=1)
    assignments = Assignment.query.filter(Assignment.deadline >= datetime.datetime.now()).all()
    timetable_c = Timetable.query.filter(Timetable.week_day == f'C{weekday[day.weekday()]}').first()
    timetable_d = Timetable.query.filter(Timetable.week_day == f'D{weekday[day.weekday()]}').first()
    return render_template('index.html', assignments=assignments, timetable_c=timetable_c, timetable_d=timetable_d, datetime=datetime, len=len)

@app.route('/forms')
def forms():
    return render_template('forms.html', datetime=datetime)

# user
@app.route('/users')
def user_list():
    users = User.query.order_by(User.created_at).all()
    return render_template('user_list.html', users=users)

@app.route('/users/<id>')
def user_detail(id):
    user = User.query.get_or_404(id)
    messages = Message.query.filter(Message.user_id == id).order_by(desc(Message.created_at)).all()
    return render_template('user_detail.html', user=user, messages=messages)

@app.get('/users/<id>/edit')
def user_edit(id):
    user = User.query.get(id)
    return render_template('user_edit.html', user=user)

@app.post('/users/<id>/update')
def user_update(id):
    user = User.query.get(id)  # 更新するデータをDBから取得
    user.name = request.form.get('name')
    user.avatar = request.form.get('avatar')
    user.group = request.form.get('group', default='G')
    user.available = request.form.get('available', default=True, type=bool)
    user.year = request.form.get('year', default=1, type=int)

    db.session.merge(user)
    db.session.commit()
    return redirect(url_for('user_list'))

@app.post('/users/<id>/delete')
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user_list'))

@app.get('/add_user')
def add_user():
    return render_template('add_user.html')

@app.post('/add_user')
def post_user():
    form_name = request.form.get('name')  # str
    form_avatar = request.form.get('avatar')  # str
    form_group = request.form.get('group', default='G')  # str
    form_avatar = request.form.get('avatar')  # str
    form_year = request.form.get('year', default=1, type=int) # int
    form_available = request.form.get('available', default=True, type=bool) #bool

    user = User(
        name=form_name,
        avatar=form_avatar,
        year=form_year,
        group=form_group,
        available=form_available,
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user_list'))

# assignment
@app.route('/assignments')
def assignment_list():
    assignments_today = Assignment.query.filter(Assignment.deadline >= datetime.date.today()).all()
    assignments_yesterday = Assignment.query.filter(Assignment.deadline < datetime.date.today()).all()
    assignments = Assignment.query.order_by(Assignment.deadline).all()
    return render_template('assignment_list.html', assignments_today=assignments_today, assignments_yesterday=assignments_yesterday, assignments=assignments)

@app.route('/assignment/<id>')
def assignment_detail(id):
    assignment = Assignment.query.get_or_404(id)
    assignments = Assignment.query.order_by(Assignment.deadline).all()
    return render_template('assignment_detail.html', assignment=assignment, assignments=assignments)

@app.get('/assignment/<id>/edit')
def assignment_edit(id):
    assignment = Assignment.query.get(id)
    assignments = Assignment.query.order_by(Assignment.deadline).all()
    return render_template('assignment_edit.html', assignments=assignments, assignment=assignment, datetime=datetime)

@app.post('/assignment/<id>/update')
def assignment_update(id):
    assignment = Assignment.query.get(id)  # 更新するデータをDBから取得
    assignment.name = request.form.get('name')  # str
    assignment.subject = request.form.get('subject')  # str
    assignment.method = request.form.get('method')  # str
    assignment.deadline = datetime.datetime.strptime(request.form.get('deadline'), '%Y-%m-%d') # str
    assignment.group = request.form.get('group', default='G')  # str
    assignment.year = request.form.get('year', default=1, type=int) # int

    db.session.merge(assignment)
    db.session.commit()
    return redirect(url_for('assignment_list'))

@app.get('/add_assignment')
def add_assignment():
    return render_template('add_assignment.html', datetime=datetime)

@app.post('/add_assignment')
def post_assignment():
    form_name = request.form.get('name')  # str
    form_subject = request.form.get('subject')  # str
    form_method = request.form.get('method')  # str
    form_deadline = request.form.get('deadline')  # str
    form_deadline = datetime.datetime.strptime(form_deadline, '%Y-%m-%d')
    form_group = request.form.get('group', default='G')  # str
    form_year = request.form.get('year', default=1, type=int) # int

    assignment = Assignment(
        name=form_name,
        subject=form_subject,
        method=form_method,
        deadline=form_deadline,
        year=form_year,
        group=form_group,
    )
    db.session.add(assignment)
    db.session.commit()
    return redirect(url_for('assignment_list'))

# quiz
@app.route('/quiz')
def quiz_list():
    quiz_today = Quiz.query.filter(Quiz.implementation_date >= datetime.date.today()).order_by(Quiz.implementation_date).all()
    quiz_yesterday = Quiz.query.filter(Quiz.implementation_date < datetime.date.today()).order_by(Quiz.implementation_date).all()
    quiz = Quiz.query.order_by(Quiz.implementation_date).all()
    return render_template('quiz_list.html', quiz_today=quiz_today, quiz_yesterday=quiz_yesterday, quiz=quiz)

@app.route('/quiz/<id>')
def quiz_detail(id):
    quiz = Quiz.query.get_or_404(id)
    quiz_all = Quiz.query.order_by(Quiz.implementation_date).all()
    return render_template('quiz_detail.html', quiz=quiz, quiz_all=quiz_all)

@app.get('/quiz/<id>/edit')
def quiz_edit(id):
    quiz = Quiz.query.get(id)
    quiz_all = Quiz.query.order_by(Quiz.implementation_date).all()
    return render_template('quiz_edit.html', quiz=quiz, quiz_all=quiz_all, datetime=datetime)

@app.post('/quiz/<id>/update')
def quiz_update(id):
    quiz = Quiz.query.get(id)  # 更新するデータをDBから取得
    quiz.name = request.form.get('name')  # str
    quiz.subject = request.form.get('subject')  # str
    quiz.implementation_date = datetime.datetime.strptime(request.form.get('implementation_date'), '%Y-%m-%d')# str
    quiz.group = request.form.get('group', default='G')  # str
    quiz.year = request.form.get('year', default=1, type=int) # int

    db.session.merge(quiz)
    db.session.commit()
    return redirect(url_for('quiz_list'))

@app.get('/add_quiz')
def add_quiz():
    return render_template('add_quiz.html', datetime=datetime)

@app.post('/add_quiz')
def post_quiz():
    form_name = request.form.get('name')  # str
    form_subject = request.form.get('subject')  # str
    form_implementation_date = request.form.get('implementation_date')  # str
    form_implementation_date = datetime.datetime.strptime(form_implementation_date, '%Y-%m-%d')
    form_group = request.form.get('group', default='G')  # str
    form_year = request.form.get('year', default=1, type=int) # int

    quiz = Quiz(
        name=form_name,
        subject=form_subject,
        implementation_date=form_implementation_date,
        year=form_year,
        group=form_group,
    )
    db.session.add(quiz)
    db.session.commit()
    return redirect(url_for('quiz_list'))

# examination
@app.route('/examinations')
def examination_list():
    examinations = Examination.query.order_by(Examination.term).all()
    return render_template('examination_list.html', examinations=examinations)

@app.get('/examination/<id>/edit')
def examination_edit(id):
    examination = Examination.query.get(id)
    examinations = Examination.query.order_by(Examination.term, Examination.subject).all()
    return render_template('examination_edit.html', examination=examination, examinations=examinations, datetime=datetime)

@app.post('/examination/<id>/update')
def examination_update(id):
    examination = Examination.query.get(id)  # 更新するデータをDBから取得
    examination.name = request.form.get('name')  # str
    examination.subject = request.form.get('subject')  # str
    examination.medium = request.form.get('medium')  # str
    examination.term = request.form.get('term')  # str
    examination.year = request.form.get('year', default=1, type=int) # int

    db.session.merge(examination)
    db.session.commit()
    return redirect(url_for('examination_list'))

@app.get('/add_examination')
def add_examination():
    return render_template('add_examination.html', datetime=datetime)

@app.post('/add_examination')
def post_examination():
    form_name = request.form.get('name')  # str
    form_subject = request.form.get('subject')  # str
    form_term = request.form.get('term')  # str
    form_medium = request.form.get('medium')  # str
    form_year = request.form.get('year', default=1, type=int) # int

    examination = Examination(
        name=form_name,
        subject=form_subject,
        term=form_term,
        medium=form_medium,
        year=form_year,
    )
    db.session.add(examination)
    db.session.commit()
    return redirect(url_for('examination_list'))

# timetable
@app.get('/add_timetable')
def add_timetable():
    return render_template('add_timetable.html', datetime=datetime)

@app.post('/add_timetable')
def post_timetable():
    form_week = request.form.get('week')  # str
    form_day = request.form.get('day')  # str
    form_first = request.form.get('first')  # str
    form_second = request.form.get('second')  # str
    form_third = request.form.get('third')  # str
    form_forth = request.form.get('forth')  # str
    form_fifth = request.form.get('fifth')  # str
    form_group = request.form.get('group', default='G')  # str
    form_year = request.form.get('year', default=1, type=int) # int

    timetable = Timetable(
        week_day=form_week + form_day,
        first=form_first,
        second=form_second,
        third=form_third,
        forth=form_forth,
        fifth=form_fifth,
        year=form_year,
        group=form_group,
    )
    db.session.add(timetable)
    db.session.commit()
    return redirect(url_for('add_timetable'))

# image
@app.get('/add_image')
def add_image():
    return render_template('add_image.html')

@app.post('/add_image')
def post_image():
    form_name = request.form.get('name')  # str
    form_avatar = request.form.get('avatar')  # str
    form_group = request.form.get('group', default='G')  # str
    form_avatar = request.form.get('avatar')  # str
    form_year = request.form.get('year', default=1, type=int) # int
    form_available = request.form.get('available', default=True, type=bool) #bool

    user = User(
        name=form_name,
        avatar=form_avatar,
        year=form_year,
        group=form_group,
        available=form_available,
    )
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('user_list'))