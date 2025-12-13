from django import forms
from .models.payment import PaymentMode, PaymentAccount

class PaymentAccountForm(forms.ModelForm):
    """
    Form to be used in the site UI for creating/editing PaymentAccount.
    Dynamically generates fields based on selected PaymentMode.
    """
    class Meta:
        model = PaymentAccount
        fields = ("name", "payment_mode", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mode = None
        # determine mode similarly to admin form
        if self.instance and self.instance.payment_mode_id:
            mode = self.instance.payment_mode
        else:
            data = self.data or {}
            pm_id = data.get("payment_mode") or self.initial.get("payment_mode")
            if pm_id:
                try:
                    mode = PaymentMode.objects.get(pk=pm_id)
                except PaymentMode.DoesNotExist:
                    mode = None

        if mode:
            fields_spec = mode.fields or {}
            required = fields_spec.get("required", [])
            optional = fields_spec.get("optional", [])
            for key in required + optional:
                initial_val = None
                if self.instance and isinstance(self.instance.data, dict):
                    initial_val = self.instance.data.get(key)
                self.fields[f"data__{key}"] = forms.CharField(
                    label=key.replace("_", " ").capitalize(),
                    required=key in required,
                    initial=initial_val,
                )

    def clean(self):
        cleaned = super().clean()
        pm = cleaned.get("payment_mode") or (self.instance and self.instance.payment_mode)
        if pm:
            fields_spec = pm.fields or {}
            allowed = set(fields_spec.get("required", []) + fields_spec.get("optional", []))
            data_obj = {}
            for k in list(self.cleaned_data.keys()):
                if k.startswith("data__"):
                    key = k.replace("data__", "")
                    val = self.cleaned_data.pop(k)
                    if val not in [None, ""]:
                        data_obj[key] = val
            # validate required
            missing = [r for r in fields_spec.get("required", []) if r not in data_obj or not data_obj[r]]
            if missing:
                raise forms.ValidationError(f"Missing required fields: {', '.join(missing)}")
            cleaned["data"] = data_obj
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.data = self.cleaned_data.get("data", {})
        if commit:
            instance.save()
        return instance

