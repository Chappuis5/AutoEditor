from django import forms

class FileUploadForm(forms.Form):
    audio = forms.FileField()
    script = forms.FileField()
