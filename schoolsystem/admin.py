from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import (
    AnyOtherPayment,
    Bill,
    CustomUser,
    EducationalResource,
    FeePayment,
    FeesStructure,
    LandingPageImage,
    LogoImage,
    NewsArticle,
    NonTeachingStaff,
    StaffGovernmentDeduction,
    Student,
    StudentResult,
    Subject,
    TeachingStaff,
    Term,
)


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["id_number", "first_name", "second_name", "surname", "phone_number"]


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """School office accounts page: the only place accounts are created or passwords reset."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ["id_number", "get_full_name", "phone_number", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["id_number", "first_name", "second_name", "surname", "phone_number"]
    ordering = ["id_number"]
    fieldsets = [
        (None, {"fields": ["id_number", "password"]}),
        ("Personal info", {"fields": ["first_name", "second_name", "surname", "phone_number"]}),
        (
            "Permissions",
            {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]},
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": [
                    "id_number",
                    "first_name",
                    "second_name",
                    "surname",
                    "phone_number",
                    "password1",
                    "password2",
                ],
            },
        ),
    ]

    PRIVILEGE_FIELDS = ["is_staff", "is_superuser", "groups", "user_permissions"]

    def get_readonly_fields(self, request, obj=None):
        """Only superusers may grant or remove privileges."""
        readonly = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            readonly += self.PRIVILEGE_FIELDS
        return readonly

    def has_change_permission(self, request, obj=None):
        """Staff with the change permission may edit accounts, but never a superuser's."""
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["student_admission_number", "full_name", "grade_level", "gender"]
    list_filter = ["grade_level", "gender"]
    search_fields = ["student_admission_number", "full_name", "parent_guardian_name"]
    filter_horizontal = ["subjects"]


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "term",
        "amount_paid",
        "payment_date",
        "payment_method",
        "balance_after",
    ]
    list_filter = ["term", "payment_method"]
    list_select_related = ["student", "term"]
    search_fields = ["student__full_name", "student__student_admission_number", "transaction_id"]

    def get_queryset(self, request):
        return super().get_queryset(request).with_running_balance()

    @admin.display(description="Balance after payment")
    def balance_after(self, payment):
        return payment.balance_after


@admin.register(EducationalResource)
class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "category", "appropriate_grade", "uploaded_at"]
    list_filter = ["subject", "category", "appropriate_grade"]
    list_select_related = ["subject"]
    search_fields = ["title", "description", "subject__name"]


@admin.register(TeachingStaff)
class TeachingStaffAdmin(admin.ModelAdmin):
    list_display = ["full_name", "tsc_number", "phone_number", "position", "employment_date"]
    list_filter = ["gender"]
    search_fields = ["tsc_number", "id_number", "full_name", "phone_number", "position"]


@admin.register(NonTeachingStaff)
class NonTeachingStaffAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone_number", "position", "department", "employment_date"]
    list_filter = ["gender", "department"]
    search_fields = ["full_name", "phone_number", "id_number", "position", "department"]


@admin.register(StaffGovernmentDeduction)
class StaffGovernmentDeductionAdmin(admin.ModelAdmin):
    list_display = ["staff_member", "staff_type", "name_of_deduction", "deducted_amount"]
    list_filter = ["staff_type", "name_of_deduction"]
    list_select_related = ["teaching_staff", "non_teaching_staff"]
    search_fields = ["teaching_staff__full_name", "non_teaching_staff__full_name"]


@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ["student", "year", "term", "examination", "score"]
    list_filter = ["year", "term", "examination"]
    list_select_related = ["student"]
    search_fields = ["student__full_name", "student__student_admission_number"]


@admin.register(AnyOtherPayment)
class AnyOtherPaymentAdmin(admin.ModelAdmin):
    list_display = ["student", "payment_for", "amount", "payment_date"]
    list_select_related = ["student"]
    search_fields = ["student__full_name", "payment_for"]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ["name_of_the_bill", "amount_paid", "date_paid"]
    search_fields = ["name_of_the_bill"]


@admin.register(LandingPageImage)
class LandingPageImageAdmin(admin.ModelAdmin):
    list_display = ["category", "date"]
    list_filter = ["category"]


admin.site.register([Subject, Term, FeesStructure, NewsArticle, LogoImage])
