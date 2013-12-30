from django import forms

class UploadFileForm(forms.Form):
    dict = forms.CharField(max_length=50)
    lesson = forms.CharField(max_length=50)
    file  = forms.FileField()
