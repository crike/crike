from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from models import Teacher, Student, Book, Lesson, Word


class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'teacher'


class UserAdmin(UserAdmin):
    inlines = (TeacherInline, )

# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Book)
admin.site.register(Lesson)
admin.site.register(Word)
