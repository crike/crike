from forms import CrikeRegistrationForm as registration_form
from forms import CrikeLoginForm as login_form
from views import get_profile


def registration(request):
    return {"registration_form": registration_form}


def login(request):
    return {"login_form": login_form}


def user_profile(request):
    profile = get_profile(request.user)
    return {'profile': profile}