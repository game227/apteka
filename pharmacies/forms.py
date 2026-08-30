from django import forms

from catalog.models import Drug, Substance
from config.form_utils import style_form
from pharmacies.models import Pharmacy, PharmacyDrugPrice, PharmacyReview


class DrugCreateForm(forms.ModelForm):
    """Dorixona xodimi katalogda yo'q dorini qo'shishi uchun — faqat
    mavjud ta'sir moddalaridan tanlaydi, yangi substance qo'shish
    huquqi berilmaydi (bu Django admin orqali, markazlashgan holda)."""

    substance = forms.ModelChoiceField(queryset=Substance.objects.order_by("name_inn"), label="Ta'sir moddasi (INN)")

    class Meta:
        model = Drug
        fields = ["trade_name", "substance", "manufacturer", "dosage_form", "dosage_strength", "reference_price"]
        labels = {
            "trade_name": "Savdo nomi",
            "manufacturer": "Ishlab chiqaruvchi",
            "dosage_form": "Shakli (tabletka, sirop...)",
            "dosage_strength": "Dozasi (masalan 500mg)",
            "reference_price": "Referent narx (ixtiyoriy)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form(self)
        self.fields["manufacturer"].required = False
        self.fields["dosage_form"].required = False
        self.fields["dosage_strength"].required = False
        self.fields["reference_price"].required = False


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
