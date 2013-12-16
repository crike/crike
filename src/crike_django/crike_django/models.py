#coding:utf-8
from django.db import models
import mongoengine

# 数据库基本模型分为word、dict、user、course、voice、image、game、video
# 当前目标：实现word、dict、user、course，其余皆往后排
# dict包含多个word，course包含多个word，user包含多个course

class Word(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    image = mongoengine.ImageField()

class BasicDict(models.Model):
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
