from flask import request, abort
from KusonukiBOT import app, db
import config, os ,datetime
from pathlib import Path
from sqlalchemy import desc, or_
from KusonukiBOT.models.user import User
from KusonukiBOT.models.assignment import Assignment
from KusonukiBOT.models.timetable import Timetable
from KusonukiBOT.models.examination import Examination
from KusonukiBOT.models.quiz import Quiz
from KusonukiBOT.models.day import Day
from KusonukiBOT.models.message import Message

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoSendMessage, AudioMessage, QuickReplyButton, MessageAction, QuickReply, FlexSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction
)


app.config.from_object('config')

line_bot_api = LineBotApi(config.ACCESS_TOKEN)
handler = WebhookHandler(config.CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    event.message.text = event.message.text.replace('　', ' ')
    message = event.message.text.split(' ')[0] or event.message.text
    args = event.message.text.split(' ')

    user_register(event.source.user_id, event, profile)
    user_updater(event.source.user_id, event, profile)
    message_log(event, profile)

    if not user_available(event.source.user_id):
        reply_message = TextSendMessage(text='使用許可がないため使用できません。')
    else:
        user = User.query.get(event.source.user_id)
        if message == 'サイト':
            reply_message = web_button(f'下記をクリックしてサイトを開きます\n〚ユーザー名〛{profile.display_name}\n〚パスワード〛{event.source.user_id[0:4]}', '', '')
        elif message == '設定':
            reply_message = web_button(f'下記をクリックして設定を行います', 'setting', event.source.user_id)
        elif message == '課題':
            if len(args) == 1:
                assignments = Assignment.query.filter(or_(Assignment.group == user.group, Assignment.group == 'ALL'), Assignment.deadline >= datetime.datetime.today()).order_by(desc(Assignment.deadline)).all()
                subject_list = []
                assignment_list = []
                for assignment in assignments:
                    if assignment.subject not in subject_list:
                        subject_list.append(assignment.subject)
                    assignment_list.append(f'⧼ {assignment.name} ⧽\n«教科» {assignment.subject}\n«手段» {assignment.method}\n«提出日時» {assignment.deadline.strftime("%m月%d日")}')
                items = [QuickReplyButton(action=MessageAction(label = subject, text = f'課題 {subject}')) for subject in subject_list]
                reply_message = TextSendMessage(text = '\n\n'.join(assignment_list) or '課題なし', quick_reply=QuickReply(items=items))
            else:
                assignments = Assignment.query.filter(or_(Assignment.group == user.group, Assignment.group == 'ALL'), Assignment.deadline >= datetime.datetime.today()).order_by(desc(Assignment.deadline)).all()
                subject_list = []
                assignment_list = []
                for assignment in assignments:
                    if assignment.subject not in subject_list:
                        subject_list.append(assignment.subject)
                    if assignment.subject == args[1]:
                        assignment_list.append(f'⧼ {assignment.name} ⧽\n«教科» {assignment.subject}\n«手段» {assignment.method}\n«提出日時» {assignment.deadline.strftime("%m月%d日")}')
                items = [QuickReplyButton(action=MessageAction(label = subject, text = f'課題 {subject}')) for subject in subject_list]
                if len(assignment_list) == 0:
                    reply_message = web_button('課題無し。\n下記から課題を追加できます。', 'assignment', '')
                else:
                    reply_message = TextSendMessage(text = '\n\n'.join(assignment_list), quick_reply=QuickReply(items=items))
        elif message == 'テスト範囲':
            type_list = ["今日", "明日", "前期中間", "前期期末", "後期中間", "後期期末"]
            if len(args) == 1:
                items = [QuickReplyButton(action=MessageAction(label = type, text = f'テスト範囲 {type}')) for type in type_list]
                reply_message = TextSendMessage(text='種類を選択してください', quick_reply=QuickReply(items=items))
            elif len(args) == 2:
                if args[1] == '今日' or args[1] == '明日':
                    day = datetime.date.today()
                    if args[1] == '明日':
                        day += datetime.timedelta(days=1)
                    quiz = Quiz.query.filter(or_(Quiz.group == user.group, Quiz.group == 'ALL'), Quiz.implementation_date == day).order_by(desc(Quiz.implementation_date)).all()
                    quiz_list = []
                    for q in quiz:
                        quiz_list.append(f'⧼ {q.name} ⧽\n«教科» {q.subject}')
                    if len(quiz_list) == 0:
                        reply_message = web_button('小テスト無し。\n下記から小テストを追加できます。', 'quiz', '')
                    else:
                        reply_message = TextSendMessage(text = '\n\n'.join(quiz_list))
                else:
                    if len(args) == 2:
                        examination = Examination.query.filter(Examination.term == args[1]).all()
                    else:
                        examination = Examination.query.filter(Examination.term == args[1], Examination.subject == args[2]).all()
                    subject_count = []
                    for exam in examination:
                        subject_count.append(exam.subject)
                    sub_count = len(set(subject_count))
                    examination_list = [[] for i in range(sub_count)]
                    subject_list = []
                    for exam in examination:
                        if exam.subject not in subject_list:
                            subject_list.append(exam.subject)
                            examination_list[subject_list.index(exam.subject)].append(f'⧼ {exam.subject} ⧽')
                            examination_list[subject_list.index(exam.subject)].append(f'«{exam.medium}» {exam.name}')
                        elif exam.subject in subject_list:
                            examination_list[subject_list.index(exam.subject)].append(f'«{exam.medium}» {exam.name}')
                    exam = []
                    for row in examination_list:
                        exam.append('\n'.join(row))
                    reply_message = TextSendMessage(text = f'［ {args[1]} の範囲 ］\n' + '\n\n'.join(exam) or '小テスト無し')
        elif message == '時間割':
            day_list = ["C月", "C火", "C水", "C木", "C金", "D月", "D火", "D水", "D木", "D金"]

            if len(args) == 1:
                items = [QuickReplyButton(action=MessageAction(label = day, text = f'時間割 {day}')) for day in day_list]
                reply_message = TextSendMessage(text='曜日を選択してください', quick_reply=QuickReply(items=items))
            elif args[1] in day_list:
                timetable = Timetable.query.filter(Timetable.group == user.group, Timetable.week_day == args[1]).first()
                if timetable is not None:
                    reply_message = TextSendMessage(text=f'［ {args[1]} の時間割 ］\n① {timetable.first}\n② {timetable.second}\n③ {timetable.third}\n④ {timetable.forth}\n⑤ {timetable.fifth}')
                else:
                    reply_message = web_button('時間割が存在しません。\n下記から時間割を追加できます。', 'timetable', '')
            else:
                reply_message = web_button('時間割が存在しません。\n下記から時間割を追加できます。', 'timetable', '')
        elif message == '予定':
            day_list = ["昨日", "今日", "明日"]
            if len(args) == 1:
                items = [QuickReplyButton(action=MessageAction(label = day, text = f'予定 {day}')) for day in day_list]
                reply_message = TextSendMessage(text='日程を選択してください', quick_reply=QuickReply(items=items))
            else:
                day = datetime.date.today()
                if args[1] == '昨日':
                    day -= datetime.timedelta(days=1)
                elif args[1] == '明日':
                    day += datetime.timedelta(days=1)

                timetable = Timetable.query.filter(Timetable.group == user.group, Timetable.week_day == args[1]).first()
                quiz = Quiz.query.filter(or_(Quiz.group == user.group, Quiz.group == 'ALL'), Quiz.implementation_date == day).order_by(desc(Quiz.subject)).all()
                quiz_list = []
                for q in quiz:
                    quiz_list.append(f'⧼ {q.name} ⧽\n«教科» {q.subject}')
                assignments = Assignment.query.filter(or_(Assignment.group == user.group, Assignment.group == 'ALL'), Assignment.deadline == day).order_by(desc(Assignment.subject)).all()
                assignment_list = []
                for assignment in assignments:
                    assignment_list.append(f'⧼ {assignment.name} ⧽\n«教科» {assignment.subject}\n«提出日時» {assignment.deadline.strftime("%m月%d日")}')

                quiz_ = '\n\n'.join(quiz_list)
                assignment_ = '\n\n'.join(assignment_list)
                reply_message = TextSendMessage(text=f"［ {args[1]} の予定 ］\n➝ 課題\n{assignment_ or '課題なし'}\n\n➝ テスト\n{quiz_ or '小テストなし'}")
        # elif message == '時間割作成':
        #     day_list = ["A", "B", "C", "D"]
        #     if len(args) == 1:
        #         items = [QuickReplyButton(action=MessageAction(label = day, text = f'時間割作成 {day}')) for day in day_list]
        #         reply_message = TextSendMessage(text='今週は何週ですか？', quick_reply=QuickReply(items=items))
        #     else:
        #         create_timetable(args[1])
        #         reply_message = TextMessage(text = f'時間割を作成しました')
        elif message == '権限編集':
            if not is_admin(event.source.user_id):
                reply_message = TextMessage(text = f'管理者のみ実行可能です')
            elif len(args) == 1:
                reply_message = TextMessage(text = f'ユーザーIDを入力してください')
            elif len(args) == 2:
                role_list = ['DEFAULT', 'EDITOR', 'ADMINISTRATOR']
                items = [QuickReplyButton(action=MessageAction(label = role, text = f'権限編集 {args[1]} {role}')) for role in role_list]
                reply_message = TextSendMessage(text='権限を選択してください', quick_reply=QuickReply(items=items))
            else:
                user = User.query.get(args[1])
                user.role = args[2]
                db.session.merge(user)
                db.session.commit()
                reply_message = TextSendMessage(text=f'{user.name} の権限を {args[2]} に変更しました')
        elif message == '削除':
            if not is_admin(event.source.user_id):
                reply_message = TextMessage(text = f'管理者のみ実行可能です')
            elif len(args) == 1:
                reply_message = TextMessage(text = f'削除するテーブルを入力してください')
            elif len(args) == 2:
                reply_message = TextMessage(text = f'削除するデータのIDを入力してください')
            else:
                if args[1] == '課題':
                    data = Assignment.query.get(args[2]).name
                    db.session.query(Assignment).filter(Assignment.id == args[2]).delete()
                elif args[1] == '小テスト':
                    data = Quiz.query.get(args[2]).name
                    db.session.query(Quiz).filter(Quiz.id == args[2]).delete()
                db.session.commit()
                reply_message = TextMessage(text = f'{data} を削除しました')
        else:
            reply_message = None


    if reply_message is not None:
        line_bot_api.reply_message(
            event.reply_token,
            reply_message
        )
    else:
        return

@handler.add(MessageEvent, message=(ImageMessage, AudioMessage))
def handle_image_audio_message(event):
    content = line_bot_api.get_message_content(event.message.id)
    if not os.path.isdir(f'./assets/{event.source.user_id}'):
        os.makedirs(f'./assets/{event.source.user_id}')
    with open(Path(f'./assets/{event.source.user_id}/{event.message.id}.jpg'), 'wb') as f:
        for c in content.iter_content():
            f.write(c)

def message_log(event, profile):
    message = Message(
        id = event.message.id,
        user_id = event.source.user_id,
        user_name = profile.display_name,
        content = event.message.text,
    )
    db.session.add(message)
    db.session.commit()

def user_available(user_id):
    user = User.query.get(user_id)
    available = user.available

    return available

def is_admin(user_id):
    user = User.query.get(user_id)
    print(user.role == 'ADMINISTRATOR')
    if user.role == 'ADMINISTRATOR':
        return True
    else:
        return False

def user_register(user_id, event, profile):
    user = User.query.get(user_id)
    if not user:
        user = User(
            id = event.source.user_id,
            name = profile.display_name,
            avatar = profile.picture_url,
            year = 1,
            group = 'G',
            available = True,
        )
        db.session.add(user)
        db.session.commit()

def user_updater(user_id, event, profile):
    user = User.query.get(user_id)
    user.id = event.source.user_id
    user.name = profile.display_name
    user.avatar = profile.picture_url
    db.session.merge(user)
    db.session.commit()

def web_button(content, flag, arg):
    url = config.WEBHOOK_URI
    link = url
    if flag == 'timetable':
        link = f"{url}/add_timetable"
    elif flag == 'assignment':
        link = f"{url}/add_assignment"
    elif flag == 'quiz':
        link = f"{url}/add_quiz"
    elif flag == 'setting':
        link = f"{url}/users/{arg}/edit"
    message_template = TemplateSendMessage(
        alt_text="くそぬきBOT管理サイト",
        template=ButtonsTemplate(
            text=content,
            title="くそぬきBOT管理サイト",
            actions=[
                URIAction(
                    uri=link,
                    label="ここをクリック"
                )
            ]
        )
    )
    return message_template

# weekday = [
#     '月', '火', '水', '木', '金', '土', '日'
# ]
# weeks = [
#     'C', 'D'
# ]

# def create_timetable(week_flag):
#     today = datetime.date.today()
#     if not week_flag == '作成しない':
#         for x in range(4):
#             for i in weeks:
#                 for j in weekday:
#                     if week_flag == 'D':
#                         day = today + datetime.timedelta(days=weekday.index(j) - today.weekday() + 7 + (7 * x))
#                         if i == 'D':
#                             day = today + datetime.timedelta(days= weekday.index(j) - today.weekday() + (7 * x))
#                     else:
#                         day = today + datetime.timedelta(days= weekday.index(j) - today.weekday() + (7 * x))
#                         if i == 'C':
#                             day = today + datetime.timedelta(days= weekday.index(j) - today.weekday() + 7 + (7 * x))
#                     if j == '土' or j == '日':
#                         break

#                     day = Day(
#                         date = day,
#                         week = i + j,
#                     )
#                     db.session.add(day)
#                     db.session.commit()