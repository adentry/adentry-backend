from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models.payment import PaymentMode, PaymentAccount


class PaymentAccountAdminForm(forms.ModelForm):
    """
    Admin form that dynamically exposes fields based on PaymentMode.fields.
    It renders the JSON values into separate form fields, and on save
    packs them back into instance.data.
    """
    class Meta:
        model = PaymentAccount
        fields = ("name", "payment_mode", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine payment_mode: prefer the instance value, fallback to posted data
        mode = None
        if self.instance and self.instance.payment_mode_id:
            mode = self.instance.payment_mode
        else:
            # when adding new object in admin, posted data might include payment_mode
            data = self.data or {}
            pm_id = data.get("payment_mode") or self.initial.get("payment_mode")
            if pm_id:
                try:
                    mode = PaymentMode.objects.get(pk=pm_id)
                except PaymentMode.DoesNotExist:
                    mode = None

        # Create dynamic fields
        if mode:
            fields_spec = mode.fields or {}
            required = fields_spec.get("required", [])
            optional = fields_spec.get("optional", [])
            for key in required + optional:
                is_required = key in required
                initial_val = None
                if self.instance and isinstance(self.instance.data, dict):
                    initial_val = self.instance.data.get(key)
                self.fields[f"data__{key}"] = forms.CharField(
                    label=key.replace("_", " ").capitalize(),
                    required=is_required,
                    initial=initial_val,
                )

    def clean(self):
        cleaned = super().clean()

        # pack dynamic data keys into self.cleaned_data['data']
        mode = None
        pm = cleaned.get("payment_mode") or (self.instance and self.instance.payment_mode)
        if pm:
            mode = pm
            fields_spec = mode.fields or {}
            allowed = set(fields_spec.get("required", []) + fields_spec.get("optional", []))
            data_obj = {}
            for k in list(self.cleaned_data.keys()):
                if k.startswith("data__"):
                    key = k.replace("data__", "")
                    val = self.cleaned_data.pop(k)
                    if val not in [None, ""]:
                        data_obj[key] = val
            # simple validation: ensure required present
            missing = []
            for req in fields_spec.get("required", []):
                if req not in data_obj or data_obj.get(req) in [None, ""]:
                    missing.append(req)
            if missing:
                raise forms.ValidationError(f"Missing required fields for {mode.name}: {', '.join(missing)}")
            cleaned["data"] = data_obj

        return cleaned

    def save(self, commit=True):
        # ensure instance.data is updated
        instance = super().save(commit=False)
        data = self.cleaned_data.get("data", {})
        instance.data = data
        if commit:
            instance.save()
        return instance


@admin.register(PaymentMode)
class PaymentModeAdmin(admin.ModelAdmin):
    list_display = ("name", "active")
    search_fields = ("name",)


@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    form = PaymentAccountAdminForm
    list_display = ("__str__", "payment_mode", "active")
    list_filter = ("payment_mode", "active")
    search_fields = ("name",)

    def get_readonly_fields(self, request, obj=None):
        # when editing, show a helpful preview of JSON data
        if obj:
            return ("preview_data",)
        return ()

    def preview_data(self, obj):
        if not obj.data:
            return "(no data)"
        lines = []
        for k, v in obj.data.items():
            lines.append(f"<b>{k}</b>: {v}")
        return format_html("<br/>".join(lines))

    preview_data.short_description = "Data (preview)"

