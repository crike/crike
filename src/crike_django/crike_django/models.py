#coding:utf-8
from django.db import models
from django.contrib.auth.models import User

from mongoengine import *

# 数据库基本模型分为word、dict、user、course、voice、image、game、video
# 当前目标：实现word、dict、user、course，其余皆往后排
# dict包含多个word，course包含多个word，user包含多个course

class Word(Document):
    name = StringField(required=True, max_length=50)
    phonetics = StringField(required=True, max_length=80)
    mean = ListField(StringField(max_length=80), required=True)
    #pos = ListField(StringField(max_length=20), required=True)
    #audio = FileField(required=True)
    #audio = StringField()
    image = FileField()

class Lesson(EmbeddedDocument):
    name = StringField(required=True)
    words = ListField(ReferenceField(Word))

class Dict(Document):
    name = StringField(required=True)
    lessons = ListField(EmbeddedDocumentField(Lesson))

    meta = {'allow_inheritance': True}

class CET4Dict(Dict):
    pass

class CET6Dict(Dict):
    pass

class WebsterDict(Dict):
    pass

# Accounts area

# This class is to keep compability with other apps
# which use original User model.
class Profile(models.Model):
    user = models.ForeignKey(User)

    @property
    def is_student(self):
        try:
            self.student
            return True
        except Student.DoesNotExist:
            return False

    @property
    def is_teacher(self):
        try:
            self.teacher
            return True
        except Student.DoesNotExist:
            return False

class Teacher(Profile):
    profile = models.ForeignKey(Profile)

    class Meta:
        db_table = 'teacher_user'

class Student(Profile):
    profile = models.ForeignKey(Profile)

    class Meta:
        db_table = 'student_user'

class TeachingAssistant(Profile):
    pass

class Course(models.Model):
    pass
