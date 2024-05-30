from django.contrib.admin import ModelAdmin, register
from django.contrib.auth import get_user_model


User = get_user_model()


@register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "last_login",
        "date_joined",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    readonly_fields = ("date_joined",)
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
    )
