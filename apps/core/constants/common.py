class MetaConstants():
    """
        Common Metadata Constants
    """
    UTF8 = 'utf-8'
    ASCII = 'ascii'
    XLSX_CONTENT = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    CSV_CONTENT = 'text/csv'
    XLSX_EXT = '.xlsx'
    CSV_EXT = '.csv'

    CSV_OR_XLSX = [XLSX_CONTENT, CSV_CONTENT]

class CommonResponse():
    """
        Common Response Constants
    """
    FETCHED = "{entity} fetched successfully."
    CREATED = "{entity} created successfully."
    UPDATED = "{entity} updated successfully."
    DELETED = "{entity} deleted successfully."
    ASSIGNED = "{assigned} assigned {assigned_to} successfully."
    UNASSIGNED = "Unassigned {assigned} from {assigned_to} successfully."
    SENT = "{entity} sent successfully."


class Entities():
    """
        Common Entity Constants
    """
    USER = "User"
    USERS = "Users"
    ROLE = "Role"
    ROLES = "Roles"
    PAGE = "Page"
    PAGES = "Pages"
    PERMISSION = "Permission"
    PERMISSIONS = "Permissions"


class Units():
    """
        Common Unit Constants
    """
    KB = 1024
    MB = 1024 * KB
    REQUEST_TIMEOUT = 30
    MINUTE = 60
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR


class Keywords():
    PRIVATE = "pvt"
    PUBLIC = "pub"