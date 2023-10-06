from django.utils.translation import gettext_lazy as _

class PermissionsTypes:
    READ_ONLY = "all"
    ADMIN = "admin"
    CREATOR = "creator"
    NONE = "none"

    PermissionChoices = [
        (READ_ONLY, _("View all content")),
        (ADMIN, _("Create/edit/delete all content")),
        (CREATOR, _("Create/edit/delete owned content")),
        (NONE, _("None")),
    ]

class UserRole:
    ADMIN = "admin"
    USER = "user"

    RoleChoices = [
        (ADMIN, _("Admin")),
        (USER, _("User"))
    ]