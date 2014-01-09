#coding:utf-8
from django.db import models
from django.contrib.auth.models import User
from djangotoolbox.fields import EmbeddedModelField, ListField

# 数据库基本模型分为word、lesson(embedded)、book、user、course、voice、image、game、video
# 当前目标：实现word、book、user、course，其余皆往后排
# book包含多个lesson，lesson包含多个word，user包含多个course

class Word(models.Model):
    name = models.CharField(max_length=50)
    phonetics = models.CharField(max_length=80)
    mean = ListField(models.CharField(max_length=80))
    #image = ImageField()

class Lesson(models.Model):
    name = models.CharField(max_length=50)
    words = ListField(models.ForeignKey('Word'))

class Book(models.Model):
    name = models.CharField(max_length=50)
    lessons = ListField(EmbeddedModelField('Lesson'))

class CET4Book(Book):
    pass

class CET6Book(Book):
    pass

class WebsterBook(Book):
    pass

# This class is to keep compability with other apps
# which use original User model.
class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    location = models.CharField(max_length=140)
    gender = models.CharField(max_length=140)
    school = models.CharField(max_length=140)
    profile_picture = models.ImageField(upload_to='thumbpath', blank=True)
    age = models.IntegerField()

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

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

# These fields use multi-table inheritance. See below urls for more details.
#   https://docs.djangoproject.com/en/1.5/topics/db/models/#multi-table-inheritance
#   http://stackoverflow.com/questions/3100521/django-registration-and-multiple-profiles
# Another related work for more performance:
#   http://onlypython.group.iteye.com/group/wiki/1519-expansion-django-user-model-by-non-profile-way
class Teacher(Profile):
    pass

class Student(Profile):
    edu_stage = models.CharField(max_length=140)

class TeachingAssistant(Profile):
    pass

class Course(models.Model):
    pass
