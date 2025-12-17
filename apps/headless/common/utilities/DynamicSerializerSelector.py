from rest_framework.serializers import ValidationError

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
        if selected_fields is None:
            return

        selected = {f.strip() for f in selected_fields if f.strip()}

        # CASE 2 — selections provided but empty → return full serializer
        if not selected:
            return

        # Always include required fields
        selected |= set(self.required_fields)

        existing = set(self.fields)

        # silently ignore invalid fields
        valid_selected = selected & existing

        # CASE 3 — after ignoring invalids, nothing left → return full serializer
        if not valid_selected:
            return

        # CASE 4 — prune unselected fields
        for field_name in existing - valid_selected:
            self.fields.pop(field_name)

