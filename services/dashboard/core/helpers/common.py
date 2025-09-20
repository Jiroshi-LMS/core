def flatten_serializer_errors(detail):
    """
        Generates human readable error messages generated from serializers.
    """
    messages = []
    for field, errors in detail.items():
        field = f"{field}: " if field != 'non_field_errors' else ''
        if isinstance(errors, (list, tuple)):
            messages.append(f"{field}{', '.join(errors)}")
        else:
            messages.append(f"{field}{errors}")
    return " | ".join(messages)