#coding:utf-8
from django.db import models
from mongoengine import *

# 数据库基本模型分为word、dict、user、course、voice、image、game、video
# 当前目标：实现word、dict、user、course，其余皆往后排
# dict包含多个word，course包含多个word，user包含多个course

class Word(Document):
    name = StringField(required=True, max_length=50)
    phonetics = StringField(required=True, max_length=80)
    mean = ListField(StringField(max_length=50))
    pos = ListField(StringField(max_length=5))
    audio = FileField(required=True)
    image = ImageField()

class BasicDict(Document):
    name = StringField(required=True)
    num = IntField()
    dictionary = ListField(ReferenceField(Word), required=True)

    meta = {'allow_inheritance': True}

class CET4Dict(BasicDict):
    pass

class CET6Dict(BasicDict):
    pass

class WebsterDict(BasicDict):
    pass

class BasicUser(models.Model):
    pass

class Teacher(BasicUser):
    pass

class TeachingAssistant(BasicUser):
    pass

class Student(BasicUser):
    pass

class Course(models.Model):
    pass
