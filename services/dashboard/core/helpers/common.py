import mimetypes
import re
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


def extract_integrity_error_context(msg):
    user_msg = "Data Integrity Error"

    # Detect UNIQUE constraint violations
    if "UNIQUE constraint failed" in msg:
        try:
            field = msg.split(":")[-1].strip()
            user_msg = f"{field} already exists."
        except Exception:
            user_msg = "Record already exists."
    # Handle duplicate key from Postgres (different message pattern)
    elif "duplicate key" in msg.lower():
        match = re.search(r"Key \(([^)]+)\)=", msg)
        if match:
            field = match.group(1)
            field = field.replace('_', ' ').capitalize()
            user_msg = f"{field} already exists."
        else:
            user_msg = "Record already exists."
    # Handle foreign key constraint failure
    elif "FOREIGN KEY constraint failed" in msg or "violates foreign key constraint" in msg:
        user_msg = "Invalid reference — related record not found."

    return user_msg


def get_presigned_object_key(
        prefix, file_name, content_type=None,
        file_ext=None, instructor_uuid=None, 
        specific_uuid=None
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