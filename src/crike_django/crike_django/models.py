from django.db import models

# 数据库基本模型分为dict、user、course、voice、image、game、video
# 当前目标：实现dict、user、course，其余皆往后排

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
