from django import forms

class CsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'accept':'.csv'})
    )