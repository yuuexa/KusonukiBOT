from flask import render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.urls import url_parse
from sqlalchemy import desc, or_, and_
from KusonukiBOT import app, db, login
from KusonukiBOT.models.user import User
from KusonukiBOT.models.assignment import Assignment
from KusonukiBOT.models.timetable import Timetable
from KusonukiBOT.models.examination import Examination
from KusonukiBOT.models.quiz import Quiz
from KusonukiBOT.models.message import Message
from KusonukiBOT.models.log import Log
import datetime
import platform

app.config['SECRET_KEY'] = "secret"

weekday = ['月', '火', '水', '木', '金', '月', '月']

today = datetime.datetime.today().date()

@login.user_loader
def load_user(id):
  return User.query.get(id)

@app.get('/login')
def login():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        return render_template('login.html')

@app.post('/login')
def post_login():
    username = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(name=username).first()
    if not user:
        return redirect('/login')
    elif user.id[0:4] == password:
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        Logging(current_user, 'LOGIN')
        return redirect(next_page)
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    Logging(current_user, 'LOGOUT')
    logout_user()
    return redirect('/login')

@app.route('/')
@login_required
def index():
    if datetime.datetime.now().hour >= 0 and datetime.datetime.now().hour < 18:
        day = today
        quiz = Quiz.query.filter(and_(Quiz.implementation_date == day, Quiz.group.in_([UserGroup(current_user), 'ALL']))).order_by(Quiz.subject, Quiz.name).all()
    else:
        day = today + datetime.timedelta(days=1)
        quiz = Quiz.query.filter(and_(Quiz.implementation_date == day, Quiz.group.in_([UserGroup(current_user), 'ALL']))).order_by(Quiz.subject, Quiz.name).all()
    assignments = Assignment.query.filter(and_(Assignment.deadline >= datetime.date.today(), Assignment.group.in_([UserGroup(current_user), 'ALL']))).order_by(Assignment.deadline, Assignment.name).all()
    assignments_today = Assignment.query.filter(and_(Assignment.deadline == today.strftime('%Y-%m-%d'), Assignment.group.in_([UserGroup(current_user), 'ALL']))).order_by(Assignment.deadline, Assignment.name).all()
    assignments_today_list = []
    for i in assignments_today:
        assignments_today_list.append(i.name)
    timetable_c = Timetable.query.filter(Timetable.week_day == f'C{weekday[day.weekday()]}', Timetable.group == UserGroup(current_user)).first()
    timetable_d = Timetable.query.filter(Timetable.week_day == f'D{weekday[day.weekday()]}', Timetable.group == UserGroup(current_user)).first()
    return render_template('index.html', assignments_today_list=', '.join(assignments_today_list), quiz=quiz, assignments=assignments, timetable_c=timetable_c, timetable_d=timetable_d, datetime=datetime, len=len)

@app.route('/forms')
@login_required
def forms():
    return render_template('forms.html', datetime=datetime)

# user
@app.route('/users')
@login_required
def user_list():
    users = User.query.order_by(User.created_at).all()
    return render_template('user_list.html', users=users)

@app.route('/users/<id>')
@login_required
def user_detail(id):
    user = User.query.get_or_404(id)
    messages = Message.query.filter(Message.user_id == id).order_by(desc(Message.created_at)).all()
    return render_template('user_detail.html', user=user, messages=messages)

@app.get('/users/<id>/edit')
@login_required
def user_edit(id):
    user = User.query.get(id)
    return render_template('user_edit.html', user=user)

@app.post('/users/<id>/update')
@login_required
def user_update(id):
    user = User.query.get(id)  # 更新するデータをDBから取得
    user.name = request.form.get('name')
    user.avatar = request.form.get('avatar')
    user.group = request.form.get('group', default='G')
    user.available = request.form.get('available', default=True, type=bool)
    user.year = request.form.get('year', default=1, type=int)

    db.session.merge(user)
    db.session.commit()
    Logging(current_user, f'USER_UPDATE {user.id}')
    return redirect(url_for('user_list'))

@app.post('/users/<id>/delete')
@login_required
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    Logging(current_user, f'USER_DELETE {user.id}')
    return redirect(url_for('user_list'))

@app.get('/add_user')
@login_required
def add_user():
    return render_template('add_user.html')

@app.post('/add_user')
@login_required
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
    assignments_today = Assignment.query.filter(and_(Assignment.deadline >= datetime.date.today(), Assignment.group.in_([UserGroup(current_user), 'ALL']))).order_by(Assignment.deadline, Assignment.name).all()
    assignments_yesterday = Assignment.query.filter(and_(Assignment.deadline < datetime.date.today(), Assignment.group.in_([UserGroup(current_user), 'ALL']))).order_by(Assignment.deadline, Assignment.name).all()
    assignments = Assignment.query.order_by(Assignment.deadline, Assignment.name).all()
    return render_template('assignment_list.html', assignments_today=assignments_today, assignments_yesterday=assignments_yesterday, assignments=assignments)

@app.route('/assignment/<id>')
def assignment_detail(id):
    assignment = Assignment.query.get_or_404(id)
    assignments = Assignment.query.order_by(Assignment.deadline, Assignment.name).all()
    return render_template('assignment_detail.html', assignment=assignment, assignments=assignments)

@app.get('/assignment/<id>/edit')
def assignment_edit(id):
    assignment = Assignment.query.get(id)
    assignments = Assignment.query.order_by(Assignment.deadline, Assignment.name).all()
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
    Logging(current_user, f'ASSIGNMENT_UPDATE {assignment.id}')
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
    Logging(current_user, f'ASSIGNMENT_ADD {assignment.id}')
    return redirect(url_for('assignment_list'))

# quiz
@app.route('/quiz')
def quiz_list():
    quiz_today = Quiz.query.filter(and_(Quiz.implementation_date >= datetime.date.today(), Quiz.group.in_([UserGroup(current_user), 'ALL']))).order_by(Quiz.implementation_date, Quiz.name).all()
    quiz_yesterday = Quiz.query.filter(and_(Quiz.implementation_date < datetime.date.today(), Quiz.group.in_([UserGroup(current_user), 'ALL']))).order_by(Quiz.implementation_date, Quiz.name).all()
    quiz = Quiz.query.order_by(Quiz.implementation_date, Quiz.name).all()
    return render_template('quiz_list.html', quiz_today=quiz_today, quiz_yesterday=quiz_yesterday, quiz=quiz)

@app.route('/quiz/<id>')
def quiz_detail(id):
    quiz = Quiz.query.get_or_404(id)
    quiz_all = Quiz.query.order_by(Quiz.implementation_date, Quiz.name).all()
    return render_template('quiz_detail.html', quiz=quiz, quiz_all=quiz_all)

@app.get('/quiz/<id>/edit')
def quiz_edit(id):
    quiz = Quiz.query.get(id)
    quiz_all = Quiz.query.order_by(Quiz.implementation_date, Quiz.name).all()
    return render_template('quiz_edit.html', quiz=quiz, quiz_all=quiz_all, datetime=datetime)

@app.post('/quiz/<id>/update')
def quiz_update(id):
    quiz = Quiz.query.get(id)  # 更新するデータをDBから取得
    quiz.name = request.form.get('name')  # str
    quiz.subject = request.form.get('subject')  # str
    form_implementation_date = request.form.get('implementation_date')  # str
    quiz.implementation_date = datetime.datetime.strptime(form_implementation_date, '%Y-%m-%d')
    quiz.group = request.form.get('group', default='G')  # str
    quiz.year = request.form.get('year', default=1, type=int) # int

    db.session.merge(quiz)
    db.session.commit()
    Logging(current_user, f'QUIZ_UPDATE {quiz.id}')
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
    Logging(current_user, f'QUIZ_ADD {quiz.id}')
    return redirect(url_for('quiz_list'))

# examination
@app.route('/examinations')
def examination_list():
    examinations = Examination.query.order_by(Examination.term, Examination.name).all()
    return render_template('examination_list.html', examinations=examinations)

@app.get('/examination/<id>/edit')
def examination_edit(id):
    examination = Examination.query.get(id)
    examinations = Examination.query.order_by(Examination.term, Examination.subject, Examination.name).all()
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
    Logging(current_user, f'EXAMINATION_UPDATE {examination.id}')
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
    Logging(current_user, f'EXAMINATION_ADD {examination.id}')
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
    Logging(current_user, f'TIMETABLE_ADD {timetable.id}')
    return redirect(url_for('add_timetable'))

# image
@app.get('/add_image')
def add_image():
    return render_template('add_image.html')

@app.post('/add_image')
def post_image():
    # form_name = request.form.get('name')  # str
    # form_avatar = request.form.get('avatar')  # str
    # form_group = request.form.get('group', default='G')  # str
    # form_avatar = request.form.get('avatar')  # str
    # form_year = request.form.get('year', default=1, type=int) # int
    # form_available = request.form.get('available', default=True, type=bool) #bool

    # user = Image(
    #     name=form_name,
    #     avatar=form_avatar,
    #     year=form_year,
    #     group=form_group,
    #     available=form_available,
    # )
    # db.session.add(user)
    # db.session.commit()
    # Logging(current_user, f'IMAGE_ADD {image.id}')
    return redirect(url_for('user_list'))

def Logging(user, content):
    if user.is_authenticated:
        log = Log(
            user_id = user.id,
            user_name = user.name,
            content = content,
        )
    else:
        log = Log(
            user_id = 'GUEST',
            user_name = 'GUEST',
            content = content,
        )
    db.session.add(log)
    db.session.commit()

def UserGroup(user):
    if user.is_authenticated:
        return user.group
    else:
        return 'G'