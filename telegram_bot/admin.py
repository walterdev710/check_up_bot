from django.contrib import admin
from telegram_bot.models import Patient, UserTest
# Register your models here.

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number")
    search_fields = ("full_name", "phone_number")
    list_filter = ("full_name",)


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display =("user", "test_name", "score", "status", "user_phone_number")

    def user_phone_number(self,obj):
        return obj.user.phone_number

    user_phone_number.short_description = "Phone Number"