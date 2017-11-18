# -*- coding=utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired, length, Regexp, EqualTo, AnyOf
from wtforms import ValidationError
from ..models import User, Question

import sys

reload(sys)
sys.setdefaultencoding('utf8')


class LoginForm(FlaskForm):
    username = StringField(u'帐号', validators=[DataRequired(), length(1, 64)], render_kw={"placeholder": '你的学号'})
    password = PasswordField(u'密码', validators=[DataRequired()], render_kw={"placeholder": '你的手机号'})
    submit = SubmitField(u'登录')


class Answer(FlaskForm):
    submit = SubmitField(u'确认本题')
    answer = SelectField(u'请选择答案', choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], coerce=unicode)


class RegistrationForm(FlaskForm):
    username = StringField(u'用户名', validators=[DataRequired(), length(2, 128)])
    password = PasswordField(u'密码', validators=[
        DataRequired(), EqualTo('password2', message=u'两次密码不一致')])
    password2 = PasswordField(u'重复密码', validators=[DataRequired()])
    register_key = StringField(u'注册码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    @staticmethod
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该账号已被使用')
