from rest_framework import serializers
from .models.payment import PaymentMode, PaymentAccount

class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ("id", "name", "description", "fields", "active")


class PaymentAccountSerializer(serializers.ModelSerializer):
    payment_mode = serializers.PrimaryKeyRelatedField(queryset=PaymentMode.objects.filter(active=True))
    data = serializers.JSONField(required=False)

    class Meta:
        model = PaymentAccount
        fields = ("id", "name", "payment_mode", "data", "active")
        read_only_fields = ("id",)

    def validate(self, attrs):
        # get mode (if not provided in partial update)
        pm = attrs.get("payment_mode") or (self.instance.payment_mode if self.instance else None)
        data = attrs.get("data") if "data" in attrs else (self.instance.data if self.instance else {})
        if pm:
            fields_spec = pm.fields or {}
            required = fields_spec.get("required", [])
            optional = fields_spec.get("optional", [])
            allowed = set(required + optional)
            # check required exist
            missing = [r for r in required if not data.get(r)]
            if missing:
                raise serializers.ValidationError({"data": f"Missing required fields for {pm.name}: {', '.join(missing)}"})
            # check unknown keys
            for key in data.keys():
                if key not in allowed:
                    raise serializers.ValidationError({"data": f"Field '{key}' not allowed for {pm.name}"})
        return attrs

    def create(self, validated_data):
        # if data missing, ensure at least empty dict
        if "data" not in validated_data:
            validated_data["data"] = {}
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # merge data instead of replacing (optional behavior)
        if "data" in validated_data:
            new_data = validated_data.pop("data") or {}
            merged = instance.data or {}
            merged.update(new_data)
            validated_data["data"] = merged
        return super().update(instance, validated_data)

