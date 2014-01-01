#coding:utf-8
from django.db import models
from mongoengine import *

# 数据库基本模型分为word、dict、user、course、voice、image、game、video
# 当前目标：实现word、dict、user、course，其余皆往后排
# dict包含多个word，course包含多个word，user包含多个course

class Word(Document):
    name = StringField(required=True, max_length=50)
    phonetics = StringField(required=True, max_length=80)
    mean = ListField(StringField(max_length=80), required=True)
    pos = ListField(StringField(max_length=20), required=True)
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
