import os

from django import forms
from django.core.exceptions import ValidationError

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Document title"}),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get("file")
        if uploaded_file is None:
            return uploaded_file

        allowed_extensions = {".pdf", ".docx", ".txt"}
        extension = os.path.splitext(uploaded_file.name)[1].lower()
        if extension not in allowed_extensions:
            raise ValidationError("Only PDF, DOCX and TXT files are allowed.")

        if uploaded_file.size > 10 * 1024 * 1024:
            raise ValidationError("File size must be 10 MB or less.")

        return uploaded_file
