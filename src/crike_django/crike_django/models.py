#coding:utf-8
from django.db import models
from django.contrib.auth.models import User

from mongoengine import *

# 数据库基本模型分为word、lesson(embedded)、book、user、course、voice、image、game、video
# 当前目标：实现word、book、user、course，其余皆往后排
# book包含多个lesson，lesson包含多个word，user包含多个course

class Word(Document):
    name = StringField(required=True, max_length=50)
    phonetics = StringField(required=True, max_length=80)
    mean = ListField(StringField(max_length=80), required=True)
    #audio = FileField(required=True)
    #audio = StringField()
    image = FileField()

class Lesson(EmbeddedDocument):
    name = StringField(required=True)
    words = ListField(ReferenceField(Word))

class Book(Document):
    name = StringField(required=True)
    lessons = ListField(EmbeddedDocumentField(Lesson))

    meta = {'allow_inheritance': True}

class CET4Book(Book):
    pass

class CET6Book(Book):
    pass

class WebsterBook(Book):
    pass

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

# These fields use multi-table inheritance. See below urls for more details.
#   https://docs.djangoproject.com/en/1.5/topics/db/models/#multi-table-inheritance
#   http://stackoverflow.com/questions/3100521/django-registration-and-multiple-profiles
class Teacher(Profile):
    pass

class Student(Profile):
    pass

class TeachingAssistant(Profile):
    pass

class Course(models.Model):
    pass
