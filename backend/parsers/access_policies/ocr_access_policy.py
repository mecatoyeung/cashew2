from django.contrib.auth.models import User

from rest_access_policy import AccessPolicy


class OCRAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["*"],
            "principal": "*",
            "effect": "allow"
        },
    ]

    @classmethod
    def scope_fields(cls, request, fields: dict, obj=None) -> dict:
        if request.user.is_superuser:
            return fields
        if request.method == "GET":
            return fields
        else:
            if request.user.has_perm("parsers.cashew_parser_management"):
                if obj.parser.owner.id == request.user.id:
                    return fields
                for permitted_user in obj.parser.permitted_users.all():
                    if permitted_user.id == request.user.id:
                        return fields
                for permitted_group in obj.parser.permitted_groups.all():
                    users = User.objects.filter(groups__id=permitted_group.id)
                    for user in users:
                        if user.id == request.user.id:
                            return fields
        fields.pop('google_vision_ocr_api_key', None)
        return fields