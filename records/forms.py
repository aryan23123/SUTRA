from django import forms

from .models import Category, InformationRecord, Tag


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class InformationRecordForm(forms.ModelForm):
    class Meta:
        model = InformationRecord
        fields = ["title", "description", "status", "category", "tags"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class RecordFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(required=False, choices=[('', 'All statuses')] + InformationRecord.STATUS_CHOICES)
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.none(), empty_label="All categories")
    tags = forms.ModelMultipleChoiceField(required=False, queryset=Tag.objects.none(), widget=forms.CheckboxSelectMultiple())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.order_by("name")
        self.fields["tags"].queryset = Tag.objects.order_by("name")
