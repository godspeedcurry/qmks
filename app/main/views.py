# -*- coding=utf-8 -*-
from . import main
from flask import render_template, flash, redirect, url_for, request, session, make_response
from flask_login import login_required, current_user, login_user, logout_user
from forms import LoginForm, Answer, RegistrationForm, QueryForm
from ..models import Marks_record, User, Question
from .. import db
from functools import wraps
import sys
import random
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')


def admin_required(func):
    @wraps(func)
    def admin(*args, **kwargs):
        per = User.query.filter_by(username=session.get('name')).first()

        if per.permission == 0:
            return func(*args, **kwargs)
        else:
            flash(u'你不是管理员')
            return redirect(url_for('main.index'))

    return admin


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.username.data
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'小e提示：仔细看看自己是否输入正确的学号与密码！')

    return render_template('main/login.html', form=form)


@main.route('/record/int:<page>', methods=['GET', 'POST'])
@login_required
def record(page):
    A = User.query.filter_by(username=session.get('name')).first()  # 从数据库中过滤出当前用户名的这一行
    a = A.list.split(',')  # 取出他的list并分片
    if A.done == 1:
        return redirect(url_for('main.mark'))
    form = Answer()
    page = int(page)
    result = Question.query.filter_by(id=a[page - 1]).first()
    if form.validate_on_submit():
        t = session.get('done')
        if t == 1:
            return redirect(url_for('main.mark'))
        a = form.answer.data
        if a == 'A':
            a = 1
        elif a == 'B':
            a = 2
        elif a == 'C':
            a = 3
        else:
            a = 4
        record = Marks_record(username=session.get('name'), Q_ID=page, time=datetime.utcnow(), Select=form.answer.data,
                              mark=(a == result.Select_Right))
        dd = Marks_record.query.filter_by(username=session.get('name'), Q_ID=page).first()
        if dd is None:
            db.session.add(record)
        else:
            db.session.delete(dd)
            db.session.commit()
            db.session.add(record)

        flash(u'答案提交成功')
    return render_template('main/record.html', result=result, page=page, form=form)


@main.route('/mark', methods=['GET', 'POST'])
@login_required
def mark():
    marks = 0
    A = User.query.filter_by(username=session.get('name')).first()
    b = A.list
    a = b.split(' ')
    for i in range(1, 21):
        results = Marks_record.query.filter_by(username=session.get('name'), Q_ID=i).order_by(Marks_record.id.desc()). \
            first()
        if results is None:
            flash(u'你还有题目没有回答,跳转至未回答页')
            return redirect(url_for('main.record', page=i))
        else:
            if results.mark == '1':
                marks += 5
    A.done = 1
    db.session.commit()
    return render_template('main/mark.html', mark=marks)


@main.route('/before_exam', methods=['GET', 'POST'])
@login_required
def before():
    return render_template('main/before_exam.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    register_key = 'magic key1'
    list1 = ['19', '20', '7', '8', '6', '13', '5', '3', '2', '14', '18', '4', '15', '10', '11', '9', '17', '12', '1', '16']
    random_list = random.sample(list1, 20)
    content = ",".join(random_list)
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.register_key.data != register_key:
            flash(u'注册码一点都不符合，请返回重试')
            return redirect(url_for('main.register'))
        else:
            if form.password.data != form.password2.data:
                flash(u'两次输入密码不一致')
                return redirect(url_for('main.register'))
            else:
                user = User(username=form.username.data, permission=1, password=form.password.data, list=content,
                            done=0)
                db.session.add(user)
                flash(u'您已经注册成功')
                return redirect(url_for('main.login'))

    return render_template('main/register.html', form=form)


@main.route('/query',methods=['GET', 'POST'])
def query():
    sno = {}
    sname = {}
    class_1 = {}
    class_2 = {}
    class_3 = {}
    class_4 = {}
    class_5 = {}
    qz = {}
    qm = {}
    group = {}
    chaiji = {}
    form = QueryForm()
    if form.validate_on_submit():
        num = form.student_number.data
        results = Marks_record.query.filter_by(username=num).order_by(Marks_record.id.asc()).first()
        sno[num] = results.sno
        sname[num] = results.sname
        class_1[num] = results.class_1
        class_2[num] = results.class_2
        class_3[num] = results.class_3
        class_4[num] = results.class_4
        class_5[num] = results.class_5
        qz[num] = results.qz
        qm[num] = results.qm
        group[num] = results.group
        chaiji[num] = results.chaiji
    return render_template('main/query.html', form=form, sno=sno, sname=sname, class_1=class_1, class_2=class_2,
                           class_3=class_3,class_4=class_4,  class_5=class_5, qz=qz, qm=qm, group=group, chaiji=chaiji
                           )





@main.route('/out', methods=['GET', 'POST'])
@admin_required
def out():
    username = []
    dict1 = {}
    dict2 = {}
    dict3 = {}
    dict4 = {}
    dict5 = {}
    count1 = 0
    count2 = 0
    name = User.query.all()
    count = len(username)
    for name in name:
        username.append(name.username)  # 将username的值存进username这个list中
    for name in username:
        marks = 0
        for i in range(1, 21):
            results = Marks_record.query.filter_by(username=name, Q_ID=i).order_by(Marks_record.id.asc()).first()
            if results is None:
                marks = 0
                break
            else:

                if results.mark == '1':
                    marks += 5
        if marks > 0:
            count1 += 1
        if marks == 0:
            count2 += 1
        dict1[name] = marks

        time1 = Marks_record.query.filter_by(username=name).order_by(Marks_record.time.asc()).limit(1).first()
        if time1 is None:
            time11 = 0
            time33 = 0
        else:
            time11 = time1.time.timetz()
            time33 = time1.time.date()
            tt1 = time1.time.timetuple()
            num1 = tt1[3]*3600+tt1[4]*60+tt1[5]
        time2 = Marks_record.query.filter_by(username=name).order_by(Marks_record.time.desc()).limit(1).first()
        if time2 is None:
            time22 = 0
            num2 = 0
            num1 = 0
        else:
            time22 = time2.time.timetz()
            tt2 = time2.time.timetuple()
            num2 = tt2[3] * 3600 + tt2[4] * 60 + tt2[5]
        dict2[name] = time11
        dict3[name] = time22
        dict4[name] = time33
        dict5[name] = num2-num1
    return render_template('main/out.html', username=username,
                           len=count, dict1=sorted(dict1.items(),
                                                   key=lambda e: e[0], reverse=True), have_done=count1,
                           not_done=count2, dict2=dict2, dict3=dict3, dict4=dict4, dict5=dict5)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经登出了系统')
    return redirect(url_for('main.login'))
