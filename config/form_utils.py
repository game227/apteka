from django import forms

_BASE_CLASS = "w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
_CHECKBOX_CLASS = "h-4 w-4 rounded border-gray-300 text-brand-600"


def style_form(form: forms.BaseForm) -> forms.BaseForm:
    """Formaning har bir maydoniga avtomatik Tailwind klasslarini qo'shadi
    — har bir formada qo'lda widget attrs yozishning oldini oladi.
    Forma __init__'ining oxirida chaqiriladi: `style_form(self)`."""
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", _CHECKBOX_CLASS)
        elif isinstance(widget, forms.RadioSelect):
            continue
        else:
            widget.attrs.setdefault("class", _BASE_CLASS)
    return form
