from django import forms

_BASE_CLASS = "w-full rounded-xl border border-white/10 bg-ink-200 px-3.5 py-2.5 text-sm text-ink-900 placeholder:text-ink-500 transition-all focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
_CHECKBOX_CLASS = "h-4 w-4 rounded border-white/20 bg-ink-200 text-brand-600 focus:ring-brand-300"


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
