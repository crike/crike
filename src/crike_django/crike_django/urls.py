
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import *
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required


from registration.forms import RegistrationFormTermsOfService
from registration.backends.simple.views import RegistrationView


from crike_django import views
from crike_django import settings
from crike_django.views import *
from crike_django.forms import *


admin.autodiscover()

#TODO rename all url names and addresses
urlpatterns = patterns('',
# accounts management for administrators
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'favicon/1.ico')),
    url(r'^auth', TemplateView.as_view(template_name='registration/auth.html'), name='auth'),
    url(r'^home/?$', login_required(HomeView.as_view()), name='home'),
    url(r'^lessonschoose$', login_required(LessonsChooseView.as_view()), name='lessonschoose'),
    url(r'^prize/delete(?:/(?P<prize_pk>.*?))?/$', login_required(PrizeDeleteView.as_view()), name='prize_delete'),
    url(r'^prize(?:/(?P<prize_pk>.*?))?/$', login_required(PrizeView.as_view()), name='prize'),
    url(r'^prize_query(?:/(?P<prize_query_pk>.*?))?/$', login_required(PrizeQueryView.as_view()), name='prize_query'),
    url(r'^admin/prize/?$', login_required(PrizeAdminView.as_view()), name='prize_admin'),
    url(r'^accounts/register/$',
          RegistrationView.as_view(form_class=CrikeRegistrationForm),
          name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^student$', login_required(StudentView.as_view()), name='student'),
    url(r'^teacher$', login_required(TeacherView.as_view()), name='teacher'),
    url(r'^word/stat$', login_required(WordStatView.as_view()), name='word_stat'),
    url(r'^user/history$', login_required(UserHistoryView.as_view()), name='user_history'),
    url(r'^user/head-sculpture$', login_required(UserHeadSculptureView.as_view()), name='user_head_sculpture'),
    url(r'^admin/students/?$', StudentsAdminView.as_view(), name='students_admin'),

    # This is an interim implement to redirect when registration complete.
    url(r'^users/(?P<username>.*)/?$', RedirectView.as_view(url=reverse_lazy('index'))),

# resource management for teachers
    url(r'^admin/books/', BooksAdminView.as_view(), name='books'),
    url(r'^admin/words/', WordsAdminView.as_view(), name='words'),
    url(r'^admin/exams/', login_required(ExamAdminView.as_view()), name='exam'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^delete/', WordDeleteView.as_view(), name='delete_word'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    #url(r'^media/audios/(?P<name>.*?)/?$', views.play_audio),
    #url(r'^media/images/(?P<name>.*?)/(?P<num>.*?)/?$', views.show_image),
    url(r'^admin/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/word/(?P<word>.*?)/?$', views.retrieve_word),
    url(r'^admin/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/?$', LessonAdminView.as_view()),
    url(r'^lesson_apply/accept/(?P<id>.*?)/?$', LessonApplyAcceptView.as_view()),
    url(r'^lesson_apply/delete/(?P<id>.*?)/?$', LessonApplyDeleteView.as_view()),
    url(r'^clean/(?P<wordname>.*?)$', views.clean_word),

# Study process for students
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/show/?$', login_required(LessonShowView.as_view()), name='lesson_show_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/pick/?$', login_required(LessonPickView.as_view()), name='lesson_pick_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/fill/?$', login_required(LessonFillView.as_view()), name='lesson_fill_view'),
    url(r'^study/book/(?P<book>.*?)/lesson/(?P<lesson>.*?)/review/?$', login_required(LessonReviewView.as_view()), name='lesson_review_view'),
    url(r'^lessonschoose/?$', login_required(LessonsChooseView.as_view()), name='lessons_choose_view'),
    url(r'^exam/(?P<id>.*?)/?$', ExamView.as_view(), name='exam_view'),
    url(r'^c2e/(?P<id>.*?)/?$', C2EView.as_view(), name='c2e_view'),
    url(r'^dictation/(?P<id>.*?)/?$', DictationView.as_view(), name='dictation_view'),
    url(r'^reading/(?P<id>.*?)/?$', ReadingView.as_view(), name='reading_view'),
    url(r'^choice/(?P<id>.*?)/?$', ChoiceView.as_view(), name='choice_view'),
    url(r'^trans/(?P<id>.*?)/?$', TransView.as_view(), name='trans_view'),
    url(r'^exam_result/(?P<id>.*?)/?$', ExamResultView.as_view(), name='exam_result_view'),

    url(r'^wordpopup/(?P<wordname>.*)$', WordPopupView.as_view(), name='word_popup_view'),

# Weixin bigger
    url(r'^bigger.*$', WeixinBiggerView.as_view(), name='weixin_bigger_view'),
    url(r'^neural-task-reply.*$', views.neural_task_reply),
    url(r'^get-neural-task-status/(?P<mediaid>.*?)$', views.get_neural_task_status),
    url(r'^neural-task-prepost.*$', views.set_neural_task_prepost),
    url(r'^neural-task-payed.*$', views.set_neural_task_payed),
    url(r'^notify-neural-task-payed.*$', views.notify_neural_task_payed),
)
