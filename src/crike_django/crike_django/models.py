#coding:utf-8
from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField
from django.conf import settings

'''
数据库基本模型分为word、lesson(embedded)、book、user、course、voice、image、game、video
当前目标：实现word、book、user、course，其余皆往后排
book包含多个lesson，lesson包含多个word，user包含多个course
'''


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


class Exam(models.Model):
    pass


# This class is to keep compability with other apps
# which use original settings.AUTH_USER_MODEL model.
class Profile(models.Model):
    # OneToOneField
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    location = models.CharField(max_length=140, blank=True, null=True)
    gender = models.CharField(max_length=140, blank=True, null=True)
    school = models.CharField(max_length=140, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='thumbpath', blank=True)
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    status = models.BooleanField(blank=True)
    last_login_ip = models.IPAddressField(blank=True, null=True)
    last_login_date = models.DateTimeField(blank=True, null=True)

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

    class Meta:
        abstract = True


# These fields use multi-table inheritance. See below urls for more details.
#   https://docs.djangoproject.com/en/1.5/topics/db/models/#multi-table-inheritance
#   http://stackoverflow.com/questions/3100521/django-registration-and-multiple-profiles
# Another related work for more performance:
#   http://onlypython.group.iteye.com/group/wiki/1519-expansion-django-user-model-by-non-profile-way
class Teacher(Profile):
    ori_school = models.CharField(max_length=140, blank=True, null=True)


class Student(Profile):
    edu_stage = models.CharField(max_length=140, blank=True, null=True)


class ExamResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    exam = models.ForeignKey(Exam)


class LessonResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    lesson = models.ForeignKey(Lesson)
    show = models.BooleanField()
    pick = models.BooleanField()
    dictation = models.BooleanField()
    fill = models.BooleanField()


class TeachingAssistant(Profile):
    pass


class Course(models.Model):
    pass
