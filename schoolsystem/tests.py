from datetime import date
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import (
    CustomUser,
    EducationalResource,
    FeePayment,
    NewsArticle,
    Student,
    StudentResult,
    Subject,
    Term,
)

PASSWORD = "a-strong-pass-123"


def create_student(admission_number="ADM001", grade="grade4", name="Achieng Otieno"):
    return Student.objects.create(
        full_name=name,
        date_of_birth=date(2014, 5, 1),
        gender="female",
        nationality="kenyan",
        student_admission_number=admission_number,
        grade_level=grade,
        emergency_contact_name="Parent",
        emergency_contact_relationship="parent or guardian",
        emergency_contact_phone="0700000000",
        parent_guardian_name="Parent",
        parent_guardian_phone="0700000000",
    )


def create_account(id_number, **extra_fields):
    return CustomUser.objects.create_user(
        id_number,
        PASSWORD,
        first_name="First",
        surname="Last",
        phone_number="0700000000",
        **extra_fields,
    )


def create_resource(title, grade, subject):
    return EducationalResource.objects.create(
        title=title,
        description=f"{title} notes",
        subject=subject,
        category="ebooks",
        appropriate_grade=grade,
    )


class AccountSecurityTests(TestCase):
    def test_self_registration_and_unverified_password_reset_are_gone(self):
        for path in ["/register/", "/resetpassword/"]:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_login_with_admission_number_ignores_case(self):
        create_student("ADM001")
        create_account("ADM001")

        response = self.client.post(reverse("login"), {"username": "adm001", "password": PASSWORD})

        self.assertRedirects(response, reverse("home"))

    def test_signed_in_users_can_change_their_password(self):
        user = create_account("ADM001")
        self.client.force_login(user)

        self.client.post(
            reverse("password_change"),
            {
                "old_password": PASSWORD,
                "new_password1": "another-strong-pass-456",
                "new_password2": "another-strong-pass-456",
            },
        )

        user.refresh_from_db()
        self.assertTrue(user.check_password("another-strong-pass-456"))


class PublicPageTests(TestCase):
    def test_public_pages_render(self):
        NewsArticle.objects.create(title="Sports day", content="Join us on Friday.")
        for name in ["home", "news", "fees_structure", "account_help", "login", "search"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_student_pages_require_login(self):
        for name in ["educational_resources", "student_results", "fee_payments"]:
            with self.subTest(page=name):
                url = reverse(name)
                self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")


class StudentRecordTests(TestCase):
    def setUp(self):
        self.student = create_student("ADM001")
        self.other_student = create_student("ADM002", name="Other Pupil")
        self.client.force_login(create_account("ADM001"))
        self.term = Term.objects.create(
            name="Term 1 2024",
            start_date=date(2024, 1, 8),
            end_date=date(2024, 4, 5),
            total_fees_payable=Decimal("30000"),
        )

    def pay(self, student, amount, method="Cash"):
        return FeePayment.objects.create(
            student=student,
            term=self.term,
            amount_paid=Decimal(amount),
            payment_date=date(2024, 1, 10),
            payment_method=method,
        )

    def test_results_show_only_the_signed_in_students(self):
        StudentResult.objects.create(
            student=self.student, year=2024, term="TERM 1", examination="MATHEMATICS", score=78
        )
        StudentResult.objects.create(
            student=self.other_student,
            year=2024,
            term="TERM 1",
            examination="MATHEMATICS",
            score=40,
        )

        response = self.client.get(reverse("student_results"))

        self.assertEqual([result.score for result in response.context["results"]], [78])

    def test_fee_payments_show_a_running_balance(self):
        self.pay(self.student, "10000")
        self.pay(self.student, "15000")
        self.pay(self.other_student, "30000")

        response = self.client.get(reverse("fee_payments"))

        balances = [payment.balance_after for payment in response.context["payments"]]
        self.assertEqual(balances, [Decimal("5000"), Decimal("20000")])

    def test_running_balance_counts_payments_that_are_filtered_out(self):
        self.pay(self.student, "10000", method="Cash")
        mpesa = self.pay(self.student, "15000", method="M-pesa Payment")

        filtered = FeePayment.objects.filter(payment_method="M-pesa Payment").with_running_balance()

        self.assertEqual(filtered.get(pk=mpesa.pk).balance_after, Decimal("5000"))

    def test_accounts_without_a_student_record_see_no_records(self):
        self.client.force_login(create_account("TSC12345"))

        response = self.client.get(reverse("fee_payments"))

        self.assertContains(response, "does not belong to a student")


class LibraryTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Mathematics")
        self.grade4 = create_resource("Fractions", "grade4", self.subject)
        self.grade7 = create_resource("Algebra", "grade7", self.subject)
        self.everyone = create_resource(
            "Study skills", EducationalResource.ALL_STUDENTS, self.subject
        )
        create_student("ADM001", grade="grade4")

    def resources_for(self, user, **params):
        self.client.force_login(user)
        return set(self.client.get(reverse("educational_resources"), params).context["resources"])

    def test_students_get_resources_for_their_grade(self):
        self.assertEqual(self.resources_for(create_account("ADM001")), {self.grade4, self.everyone})

    def test_students_can_browse_the_whole_library(self):
        resources = self.resources_for(create_account("ADM001"), all="1")

        self.assertEqual(resources, {self.grade4, self.grade7, self.everyone})

    def test_staff_see_the_whole_library(self):
        resources = self.resources_for(create_account("TSC12345"))

        self.assertEqual(resources, {self.grade4, self.grade7, self.everyone})

    def test_media_kind_follows_the_file_extension(self):
        cases = {"notes.PDF": "download", "chart.png": "image", "lesson.mp4": "video", "": ""}
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.grade4.file.name = name
                self.assertEqual(self.grade4.media_kind, expected)


class SearchTests(TestCase):
    def setUp(self):
        subject = Subject.objects.create(name="Science")
        create_resource("Science experiments", "grade4", subject)
        NewsArticle.objects.create(title="Science fair", content="Projects on display.")
        student = create_student("ADM001")
        other = create_student("ADM002", name="Other Pupil")
        for pupil, comment in [(student, "Science star"), (other, "Science needs work")]:
            StudentResult.objects.create(
                student=pupil,
                year=2024,
                term="TERM 1",
                examination="SCIENCE AND TECHNOLOGY",
                score=70,
                teacher_comments=comment,
            )

    def search(self):
        return self.client.get(reverse("search"), {"q": "science"}).context["results"]

    def test_visitors_only_search_public_pages(self):
        self.assertEqual(set(self.search()), {"fees_structures", "news"})

    def test_students_also_search_the_library_and_their_own_results(self):
        self.client.force_login(create_account("ADM001"))

        results = self.search()

        self.assertEqual(results["resources"].count(), 1)
        comments = [result.teacher_comments for result in results["student_results"]]
        self.assertEqual(comments, ["Science star"])

    def test_an_empty_search_does_not_fail(self):
        response = self.client.get(reverse("search"), {"q": "  "})

        self.assertContains(response, "Type what you are looking for")


class ModelRuleTests(TestCase):
    def test_religious_education_options_are_distinct(self):
        values = [value for value, _ in StudentResult.EXAMINATION_CHOICES]

        self.assertEqual(len(values), len(set(values)))


class AdminPrivilegeTests(TestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            "admin", PASSWORD, first_name="Head", surname="Admin", phone_number="0700000000"
        )
        self.office = create_account("office", is_staff=True)
        self.office.user_permissions.add(
            *Permission.objects.filter(codename__in=["view_customuser", "change_customuser"])
        )
        self.pupil = create_account("adm001")
        self.client.force_login(self.office)

    def test_office_staff_cannot_edit_a_superuser(self):
        url = reverse("admin:schoolsystem_customuser_change", args=[self.superuser.pk])

        response = self.client.post(url, {"id_number": "hijacked"})

        self.assertEqual(response.status_code, 403)
        self.superuser.refresh_from_db()
        self.assertEqual(self.superuser.id_number, "admin")

    def test_office_staff_cannot_grant_privileges(self):
        url = reverse("admin:schoolsystem_customuser_change", args=[self.pupil.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="is_staff"')
        self.assertNotContains(response, 'name="is_superuser"')

    def test_staff_without_the_change_permission_cannot_edit_accounts(self):
        self.office.user_permissions.clear()
        url = reverse("admin:schoolsystem_customuser_change", args=[self.pupil.pk])

        self.assertEqual(self.client.get(url).status_code, 403)
