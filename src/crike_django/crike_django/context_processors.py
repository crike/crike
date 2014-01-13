from forms import CrikeRegistrationForm as registration_form
from forms import CrikeLoginForm as login_form


def registration(request):
    return {"registration_form": registration_form}


def login(request):
    return {"login_form": login_form}
