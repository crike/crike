from django.db import models

# ���ݿ����ģ�ͷ�Ϊdict��user��course��voice��image��game��video
# ��ǰĿ�꣺ʵ��dict��user��course�������������

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
