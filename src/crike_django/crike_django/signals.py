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