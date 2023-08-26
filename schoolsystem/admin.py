
from django.contrib import admin
from django.db.models import Q
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import Student, Subject,CustomUser,TeachingStaff,NonTeachingStaff,New,Bill,StaffGovernmentDeduction,StudentResult, AnyOtherPayment,Term_or_semester,FeePayment,EducationalResource,FeesStructure,landingPageImage


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id_number', 'first_name', 'second_name', 'surname', 'phone_number')
    search_fields = ('id_number', 'first_name', 'second_name', 'surname', 'phone_number')
    ordering = ('id_number',)  # Use a valid field for ordering
    fieldsets = (
        (None, {'fields': ('id_number', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'second_name', 'surname', 'phone_number')}),
        ('Permissions', {'fields': ('is_active','is_staff', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('id_number', 'first_name', 'second_name', 'surname', 'phone_number', 'password1', 'password2'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # If the current user is not a superuser, make certain fields read-only
        if not request.user.is_superuser:
            return ( 'groups', )
        return self.readonly_fields

    def has_change_permission(self, request, obj=None):
        # If the current user is not a superuser and obj is not None (i.e., editing an existing user)
        if not request.user.is_superuser and obj:
            # Allow users with change permissions to modify the user if they are not superusers
            if obj.is_superuser:
                return False  # Prevent changing superuser permissions
            return True
        return super().has_change_permission(request, obj)

    def get_fields(self, request, obj=None):
        # If the current user is a staff user, remove is_superuser field
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser and 'is_superuser' in fields:
            fields.remove('is_superuser')
        return fields





class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'date_of_birth', 'gender', 'nationality', 'student_admission_number',
        'grade_level', 'enrollment_date', 'clubs_organizations', 'sports_participation',
        'awards', 'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
        'parent_guardian_name', 'parent_guardian_phone', 'date_created', 'date_updated'
    )
    list_filter = ('gender', 'grade_level')
    search_fields = (
        'full_name', 'date_of_birth', 'gender', 'nationality', 'student_admission_number',
        'grade_level', 'subjects__name', 'enrollment_date', 'clubs_organizations', 'sports_participation',
        'awards', 'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
        'parent_guardian_name', 'parent_guardian_phone'
    )

admin.site.register(Student, StudentAdmin)




class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('get_student_admission_number', 'get_student_full_name', 'term_or_semester_name', 'amount_paid', 'payment_date', 'payment_method', 'transaction_id', 'notes', 'balance')
    search_fields = ['student__full_name', 'student__student_admission_number', 'amount_paid', 'transaction_id'] 

    def get_student_full_name(self, obj):
        return obj.student.full_name
    
    def get_student_admission_number(self, obj):
        return obj.student.student_admission_number

    get_student_full_name.short_description = 'Student Full Name'
    get_student_admission_number.short_description = 'Admission Number'

admin.site.register(FeePayment, FeePaymentAdmin)



class EducationalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'category', 'appropriate_grade', 'uploaded_at')
    list_filter = ('subject', 'category', 'appropriate_grade')
    search_fields = ('title', 'description', 'subject__name', 'category', 'appropriate_grade', 'link')

admin.site.register(EducationalResource, EducationalResourceAdmin)



admin.site.register(Subject)


admin.site.register(FeesStructure)



class TeachingStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'phone_number', 'position', 'employment_date')
    list_filter = ('gender',)
    search_fields = (
        'tsc_number', 'id_number', 'full_name', 'phone_number', 'position',
        'awards', 'professional_organizations', 'employment_date'
    )

admin.site.register(TeachingStaff, TeachingStaffAdmin)



class NonTeachingStaffAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'gender', 'phone_number', 'position', 'department', 'employment_date')
    list_filter = ('gender', 'department')
    search_fields = (
        'full_name', 'gender', 'phone_number', 'id_number', 'position', 'department',
        'employment_duration', 'employment_date'
    )

admin.site.register(NonTeachingStaff, NonTeachingStaffAdmin)



admin.site.register(New)



class BillAdmin(admin.ModelAdmin):
    list_display = ('name_of_the_bill', 'amount_payed_for_the_bill', 'date_payed')
    search_fields = ('name_of_the_bill', 'amount_payed_for_the_bill', 'date_payed')

admin.site.register(Bill, BillAdmin)



class StaffGovernmentDeductionAdmin(admin.ModelAdmin):
    list_display = ('staff_type', 'staff_name_or_non_teaching_staff_name', 'deducted_amount', 'name_of_deduction', 'date_deducted')
    search_fields = ('staff_name__full_name', 'non_teaching_staff_name__full_name', 'name_of_deduction', 'date_deducted')

    def staff_name_or_non_teaching_staff_name(self, obj):
        if obj.staff_type == obj.TEACHING_STAFF:
            return obj.staff_name.full_name if obj.staff_name else 'Not specified'
        elif obj.staff_type == obj.NON_TEACHING_STAFF:
            return obj.non_teaching_staff_name.full_name if obj.non_teaching_staff_name else 'Not specified'
        return 'Not specified'
    staff_name_or_non_teaching_staff_name.short_description = 'Staff Name'

admin.site.register(StaffGovernmentDeduction, StaffGovernmentDeductionAdmin)




class StudentResultAdmin(admin.ModelAdmin):
    list_display = ('year', 'student_admission','student_full_name', 'term_or_semester_name', 'examination', 'score')
    list_filter = ('year', 'term_or_semester_name', 'examination')
    search_fields = (
        'year', 'student__full_name', 'term_or_semester_name', 'examination', 'score',
        'teacher_comments', 'date_uploaded'
    )

    def student_admission(self, obj):
        return obj.student
    student_admission.short_description = 'Student Admission'


    def student_full_name(self, obj):
        return obj.student.full_name
    student_full_name.short_description = 'Student Full Name'

admin.site.register(StudentResult, StudentResultAdmin)




admin.site.register(Term_or_semester)


@admin.register(landingPageImage)
class LandingPageImageAdmin(admin.ModelAdmin):
    list_display = ('landing_page_picture_category', 'date')
    list_filter = ('landing_page_picture_category', 'date')
    search_fields = ('landing_page_picture_category', 'date')


class AnyOtherPaymentAdmin(admin.ModelAdmin):
    list_display = ('student_admission', 'student_full_name', 'payment_for', 'amount', 'payment_date')
    search_fields = ('student__full_name', 'payment_for')
    
    def student_admission(self, obj):
        return obj.student
    student_admission.short_description = 'Student Admission'

    def student_full_name(self, obj):
        return obj.student.full_name
    student_full_name.short_description = 'Student Full Name'

admin.site.register(AnyOtherPayment, AnyOtherPaymentAdmin)
