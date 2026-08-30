from django import forms

from catalog.models import Drug
from config.form_utils import style_form
from pharmacies.models import Pharmacy, PharmacyDrugPrice, PharmacyReview


class PriceForm(forms.ModelForm):
    drug = forms.ModelChoiceField(queryset=Drug.objects.select_related("substance"), label="Dori")

    class Meta:
        model = PharmacyDrugPrice
        fields = ["drug", "price", "in_stock"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class CsvUploadForm(forms.Form):
    file = forms.FileField(label="CSV fayl")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class PharmacyForm(forms.ModelForm):
    class Meta:
        model = Pharmacy
        fields = ["name", "address", "lat", "lng", "phone", "work_hours"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)


class PharmacyReviewForm(forms.ModelForm):
    class Meta:
        model = PharmacyReview
        fields = ["rating", "comment"]
        widgets = {"rating": forms.RadioSelect(choices=[(i, f"{i}★") for i in range(1, 6)])}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
