import mimetypes
from core.constants import PresignedPrefix

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


def get_presigned_object_key(
        prefix, file_name, 
        file_ext=None, instructor_uuid=None, 
        specific_uuid=None, content_type=None
    ):
    extension = None
    if file_ext:
        extension = f".{file_ext}"
    elif content_type:
        extension = mimetypes.guess_extension(content_type)
    else:
        raise ValueError("Either file_ext or content_type must be provided to generate object key.")

    object_key = f"{prefix}/"
    if instructor_uuid:
        object_key += f"{instructor_uuid}/"
    if specific_uuid:
        object_key += f"{specific_uuid}/"
    object_key += f"{file_name}{extension}"
    return object_key