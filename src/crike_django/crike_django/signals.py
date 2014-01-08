#coding:utf-8

from registration.signals import user_registered
from models import Profile, Teacher, Student

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

user_registered.connect(create_profile)