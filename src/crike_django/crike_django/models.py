#coding:utf-8

import datetime

from django.db import models
from djangotoolbox.fields import EmbeddedModelField, ListField
from django.conf import settings
from django.core.cache import cache

'''
数据库基本模型分为word、lesson(embedded)、book、user、course、voice、image、game、video
当前目标：实现word、book、user、course，其余皆往后排
book包含多个lesson，lesson包含多个word，user包含多个course
'''

class Prize(models.Model):
    '''
    People buy prize with points.
    '''
    name = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=50, default='prize')
    tag = models.CharField(max_length=50, default='prize')
    value = models.IntegerField(default=10) # XXX
    amount = models.IntegerField(default=1)


class PrizeQuery(models.Model):
    '''
    When a person buys a prize, system generates a prize
    query, and wait for teacher to give the student a real
    prize. (maybe pending in a wait queue)
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField(auto_now_add=True)
    prize = models.ForeignKey('Prize')
    tag = models.CharField(max_length=50, default='normal')
    amount = models.IntegerField(default=1) # XXX
    # value may change, use the value of current time
    value = models.IntegerField(default=0)
    done = models.BooleanField(default=False)


class ClassRelation(models.Model):
    '''
           1    n
    Lesson ------ Teacher
           1    n
    Lesson ------ User (standing for student/teacher)
    '''
    name = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    lesson = models.ForeignKey("Lesson")
    teachers = models.ManyToManyField("Teacher")
    students = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Word(models.Model):
    name = models.CharField(max_length=50, unique=True)
    phonetics = models.CharField(max_length=50)
    mean = ListField(models.CharField(max_length=100))
    example = models.CharField(max_length=500,blank=True)
    example_t = models.CharField(max_length=500,blank=True)
    
    def __unicode__(self):
        return self.name

class Choicesingle(models.Model):
    name = models.CharField(max_length=100, blank=True)
    question = models.TextField(max_length=500)
    answers = ListField(models.CharField(max_length=500))
    rightindex = models.IntegerField()
    
    def __unicode__(self):
        return self.name

class Reading(models.Model):
    name = models.CharField(max_length=100)
    article = models.TextField()
    questions = ListField(EmbeddedModelField('Choicesingle'))
    
    def __unicode__(self):
        return self.name

class LessonApply(models.Model):
    '''
    When a person applies a prize, system generates a lesson
    apply, and wait for teacher to approve the apply, then 
    this lesson will show up in the person's home page
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateField(auto_now_add=True)
    lesson = models.ForeignKey('Lesson')
    tag = models.CharField(max_length=50, default='normal')
    done = models.BooleanField(default=False)

class Lesson(models.Model):
    name = models.CharField(max_length=50)
    book = models.ForeignKey('Book')
    words = ListField(models.ForeignKey('Word'))
    tag = models.CharField(max_length=50, blank=True, default='new')

    def __unicode__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=50)
    lessons = ListField(EmbeddedModelField('Lesson'))
    is_public = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class Exam(models.Model):
    name = models.CharField(max_length=50)
    lessons = ListField(EmbeddedModelField('Lesson'))
    choices = ListField(EmbeddedModelField('Choicesingle'))
    readings = ListField(EmbeddedModelField('Reading'))
    totalpoints = models.IntegerField(blank=True, default=0)
    withtrans = models.BooleanField(default=True)
    tag = models.CharField(max_length=50, blank=True, null=True)


# This class is to keep compability with other apps
# which use original settings.AUTH_USER_MODEL model.
class Profile(models.Model):
    # OneToOneField
    location = models.CharField(max_length=140, blank=True, null=True)
    gender = models.CharField(max_length=140, blank=True, null=True)
    school = models.CharField(max_length=140, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='head_sculpture', blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    status = models.BooleanField(blank=True)
    last_login_ip = models.IPAddressField(blank=True, null=True)
    last_login_date = models.DateTimeField(blank=True, null=True)
    is_human = models.BooleanField()
    usable_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    biggest_points = models.IntegerField(default=0)
    last_visit = models.DateTimeField(auto_now=True, null=True)
    study_cright = models.IntegerField(default=0)
    exam_cright = models.IntegerField(default=0)

    # Profile Statistics Area:
    longest_streak = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    words_learnt = models.IntegerField(default=0)
    words_mistake_num = models.IntegerField(default=0)
    words_correct_num = models.IntegerField(default=0)
    lessons_learnt = models.IntegerField(default=0)
    books_learnt = models.IntegerField(default=0)

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

    def point_add(self, point):
        if self.usable_points + point < 0:
            return False
        self.usable_points += point
        if point > 0:
            self.total_points += point
        if self.biggest_points < point:
            self.biggest_points = point
        return True

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(
                         seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

    def __unicode__(self):
        return u'Profile of user: %s' % self.user
    
    class Meta:
        abstract = True



# These fields use multi-table inheritance. See below urls for more details.
#   https://docs.djangoproject.com/en/1.5/topics/db/models/#multi-table-inheritance
#   http://stackoverflow.com/questions/3100521/django-registration-and-multiple-profiles
# Another related work for more performance:
#   http://onlypython.group.iteye.com/group/wiki/1519-expansion-django-user-model-by-non-profile-way
class Teacher(Profile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="teacher")
    ori_school = models.CharField(max_length=140, blank=True, null=True)


class Student(Profile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="student")
    edu_stage = models.CharField(max_length=140, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)


class StatBase(models.Model):
    date = models.DateField(auto_now_add=True)
    time_added = models.DateTimeField(auto_now_add=True, auto_now=True)
    time_modified = models.DateTimeField(auto_now_add=True)
    time_deleted = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return str(self.time_added)

    class Meta:
        abstract = True


class RecorderBase(models.Model):
    date = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return str(self.date)

    class Meta:
        abstract = True


# Record events like `someone answered a question about a word`, etc.
class WordEventRecorder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='word_event_user')
    word = models.ForeignKey(Word, blank=True, null=True, related_name='word_event_word')
    lesson = models.ForeignKey(Lesson, blank=True, null=True)
    mistake_num = models.IntegerField(default=0)
    correct_num = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=140, blank=True, null=True)


# Record events like `lesson done`, `book done`, etc.
class EventRecorder(RecorderBase):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    done_lesson = models.ForeignKey(Lesson, blank=True, null=True)
    done_book = models.ForeignKey(Book, blank=True, null=True)
    done_exam = models.ForeignKey(Exam, blank=True, null=True)


# A student would have many stats. Each stat is corresponding to a date.
class StudentStat(models.Model):
    student = models.ForeignKey(Student)
    mistake_num = models.IntegerField(default=0)
    correct_num = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)


class ExamStat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    exam = models.ForeignKey(Exam)
    # don't give it a default, None means this exam hasn't been taken
    score = models.IntegerField(blank=True, null=True) 
    score_words = models.IntegerField(blank=True, default=0)
    score_trans = models.IntegerField(blank=True, default=0)
    score_choices = models.IntegerField(blank=True, default=0)
    score_readings = models.IntegerField(blank=True, default=0)
    timestamp = models.DateTimeField(auto_now=True)
    tag = models.CharField(max_length=140, blank=True, null=True)


class WordStat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    word = models.ForeignKey(Word)
    lesson = models.ForeignKey(Lesson, blank=True, null=True)
    mistake_num = models.IntegerField(default=0)
    correct_num = models.IntegerField(default=0)
    tag = models.CharField(max_length=140, blank=True, null=True)


class LessonStat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    lesson = models.ForeignKey(Lesson)
    show = models.IntegerField(default=0)
    pick = models.IntegerField(default=0)
    review = models.IntegerField(default=0)
    fill = models.IntegerField(default=0)
    percent = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)
    selected = models.BooleanField(default=False)

    def __unicode__(self):
        return u'User %s show %d pick %d fill %d review %d' % (self.user, self.show, self.pick, self.review, self.fill)


class TeachingAssistant(Profile):
    pass


# Course: CET4, CET6, Grade One, etc.
# A lesson should be corresponding to several courses.
class Course(models.Model):
    pass


from registration.signals import user_registered
#from models import Profile, Teacher, Student

def create_profile(sender, instance, request, **kwargs):

    try:
        user_type = request.POST['usertype'].lower()
        if user_type == "teacher": #user .lower for case insensitive comparison
            Teacher(user = instance).save()
        elif user_type == "student":
            Student(user = instance).save()
        else:
            Profile(user = instance).save() #Default create - might want to raise error instead
    except KeyError:
        Profile(user = instance).save() #Default create just a profile


# This callback is called by a registration signal.
# XXX move this function to a meaningful file.
def register_with_profile(sender, user, request, **kwargs):
    profile = Profile(user=user)
    profile.is_human = bool(request.POST["is_human"])
    profile.save()


# This callback is called by a registration signal.
# XXX move this function to a meaningful file.
def register_with_student_profile(sender, user, request, **kwargs):
    profile = Student(user=user)
    profile.save()


# Now a registered user is always a student.
user_registered.connect(register_with_student_profile)
