#coding:utf-8
from django.db import models
import mongoengine as me

# 数据库基本模型分为word、dict、user、course、voice、image、game、video
# 当前目标：实现word、dict、user、course，其余皆往后排
# dict包含多个word，course包含多个word，user包含多个course

class Word(me.Document):
    name = me.StringField(required=True, max_length=50)
    phonetic_symbol = me.StringField(required=True, max_lenght=80)
    mean = me.ListField(me.StringField(max_length=50))
    pos = me.ListField(me.StringField(max_length=5))
    audio = me.FileField(required=True)
    image = me.ImageField()

class BasicDict(models.Model):
    name = me.StringField(required=True)
    num = me.IntField()
    dictionary = me.ListField(Word(), required=True)
    pass

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
