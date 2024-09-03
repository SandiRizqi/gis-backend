# forms.py
from django import forms

class TMATLocationsCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="CSV File", help_text="Upload a CSV file with TMAT_LOCATIONS data.")


class TMATLocationDataCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')
