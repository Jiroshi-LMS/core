from rest_framework.serializers import ValidationError

class DynamicFieldsMixin:
    """
    Mixin for serializers, to help with dynamic field selection
    """
    required_fields = []  # extend if needed

    def __init__(self, *args, **kwargs):
        selected_fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        # CASE 1 — frontend did NOT provide selections → return full serializer
        # selected_fields = None
        if selected_fields is None:
            return

        selected = {f.strip() for f in selected_fields if f.strip()}

        # CASE 2 — selections provided but empty → return full serializer
        if not selected:
            return

        # Always include required fields
        selected |= set(self.required_fields)

        existing = set(self.fields)
        invalid = selected - existing

        # CASE 3 — invalid selections → notify instead of silently returning full serializer
        if invalid:
            raise ValidationError(f"Invalid selections: {', '.join(invalid)}")

        # CASE 4 — valid selections → prune rest
        for field_name in existing - selected:
            self.fields.pop(field_name)
