from datetime import timedelta

import pyotp
import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from pharmacies.models import Pharmacy, PharmacyInvite


@pytest.fixture
def pharmacy(db):
    return Pharmacy.objects.create(name="Shifo Apteka", address="Toshkent, Chilonzor", lat=41.29, lng=69.20)


@pytest.fixture
def staff_user(db, pharmacy):
    return User.objects.create_user(
        username="dilnoza", password="demo12345", role=UserRole.PHARMACY_STAFF, pharmacy=pharmacy,
    )


@pytest.fixture
def plain_user(db):
    return User.objects.create_user(username="aziz", password="demo12345")


def test_login_locks_out_after_5_failed_attempts(client, plain_user):
    from django.core.cache import cache

    cache.clear()
    for _ in range(5):
        client.post(reverse("accounts:login"), {"username": "aziz", "password": "notogri"})

    response = client.post(
        reverse("accounts:login"), {"username": "aziz", "password": "demo12345"}, follow=True
    )
    assert "_auth_user_id" not in client.session
    error_messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert any("Juda ko'p noto'g'ri urinish" in m for m in error_messages)
    cache.clear()


def test_login_succeeds_within_attempt_limit(client, plain_user):
    from django.core.cache import cache

    cache.clear()
    for _ in range(3):
        client.post(reverse("accounts:login"), {"username": "aziz", "password": "notogri"})

    response = client.post(reverse("accounts:login"), {"username": "aziz", "password": "demo12345"})
    assert "_auth_user_id" in client.session
    cache.clear()


@pytest.fixture
def totp_user(db):
    secret = pyotp.random_base32()
    user = User.objects.create_user(username="totpuser", password="demo12345", totp_secret=secret, totp_enabled=True)
    return user


def test_login_with_totp_enabled_requires_second_step(client, totp_user):
    response = client.post(reverse("accounts:login"), {"username": "totpuser", "password": "demo12345"})
    assert response.status_code == 302
    assert response.url == reverse("accounts:totp_verify")
    assert "_auth_user_id" not in client.session
    assert client.session["pre_2fa_user_id"] == totp_user.pk


def test_totp_verify_with_correct_code_logs_in(client, totp_user):
    client.post(reverse("accounts:login"), {"username": "totpuser", "password": "demo12345"})
    code = pyotp.TOTP(totp_user.totp_secret).now()
    response = client.post(reverse("accounts:totp_verify"), {"code": code})
    assert response.status_code == 302
    assert "_auth_user_id" in client.session
    assert "pre_2fa_user_id" not in client.session


def test_totp_verify_with_wrong_code_does_not_log_in(client, totp_user):
    client.post(reverse("accounts:login"), {"username": "totpuser", "password": "demo12345"})
    response = client.post(reverse("accounts:totp_verify"), {"code": "000000"})
    assert "_auth_user_id" not in client.session
    error_messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert any("noto'g'ri" in m for m in error_messages)


def test_totp_verify_locks_out_after_5_failed_attempts(client, totp_user):
    from django.core.cache import cache

    cache.clear()
    client.post(reverse("accounts:login"), {"username": "totpuser", "password": "demo12345"})
    for _ in range(5):
        client.post(reverse("accounts:totp_verify"), {"code": "000000"})

    real_code = pyotp.TOTP(totp_user.totp_secret).now()
    response = client.post(reverse("accounts:totp_verify"), {"code": real_code}, follow=True)
    assert "_auth_user_id" not in client.session
    error_messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert any("Juda ko'p noto'g'ri urinish" in m for m in error_messages)
    cache.clear()


def test_totp_setup_enables_2fa_with_correct_code(client, plain_user):
    client.force_login(plain_user)
    client.get(reverse("accounts:totp_setup"))
    plain_user.refresh_from_db()
    assert plain_user.totp_secret

    code = pyotp.TOTP(plain_user.totp_secret).now()
    response = client.post(reverse("accounts:totp_setup"), {"code": code})
    assert response.status_code == 302
    plain_user.refresh_from_db()
    assert plain_user.totp_enabled is True


def test_totp_setup_rejects_wrong_code(client, plain_user):
    client.force_login(plain_user)
    client.get(reverse("accounts:totp_setup"))
    client.post(reverse("accounts:totp_setup"), {"code": "000000"})
    plain_user.refresh_from_db()
    assert plain_user.totp_enabled is False


def test_totp_disable_requires_correct_password(client, totp_user):
    client.force_login(totp_user)
    client.post(reverse("accounts:totp_disable"), {"password": "notogri"})
    totp_user.refresh_from_db()
    assert totp_user.totp_enabled is True

    client.post(reverse("accounts:totp_disable"), {"password": "demo12345"})
    totp_user.refresh_from_db()
    assert totp_user.totp_enabled is False
    assert totp_user.totp_secret == ""


def test_register_creates_plain_user_and_logs_in(client, db):
    response = client.post(
        reverse("accounts:register"),
        {"username": "yangi", "first_name": "Yangi", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="yangi")
    assert user.role == UserRole.USER
    assert user.pharmacy_id is None
    assert response.status_code == 302
    assert "_auth_user_id" in client.session


def test_register_with_valid_invite_grants_pharmacy_staff(client, pharmacy):
    invite = PharmacyInvite.objects.create(pharmacy=pharmacy)
    url = f"{reverse('accounts:register')}?invite={invite.token}"
    client.post(
        url,
        {"username": "xodim", "first_name": "Xodim", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="xodim")
    assert user.role == UserRole.PHARMACY_STAFF
    assert user.pharmacy_id == pharmacy.id

    invite.refresh_from_db()
    assert invite.used_by_id == user.id
    assert invite.is_valid is False


def test_register_with_expired_invite_falls_back_to_plain_user(client, pharmacy):
    invite = PharmacyInvite.objects.create(pharmacy=pharmacy, expires_at=timezone.now() - timedelta(days=1))
    url = f"{reverse('accounts:register')}?invite={invite.token}"
    client.post(
        url,
        {"username": "kech", "first_name": "Kech", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="kech")
    assert user.role == UserRole.USER
    assert user.pharmacy_id is None


def test_register_with_already_used_invite_falls_back_to_plain_user(client, pharmacy, plain_user):
    invite = PharmacyInvite.objects.create(pharmacy=pharmacy, used_by=plain_user)
    url = f"{reverse('accounts:register')}?invite={invite.token}"
    client.post(
        url,
        {"username": "ikkinchi", "first_name": "Ikkinchi", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="ikkinchi")
    assert user.role == UserRole.USER


def test_register_without_accepting_terms_is_blocked(client, db):
    response = client.post(
        reverse("accounts:register"),
        {"username": "shartsiz", "first_name": "Shartsiz", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345"},
    )
    assert response.status_code == 200
    assert not User.objects.filter(username="shartsiz").exists()
    assert "terms_accepted" in response.context["form"].errors


def test_register_sets_accepted_terms_at(client, db):
    client.post(
        reverse("accounts:register"),
        {"username": "roziboldi", "first_name": "Rozi", "email": "test@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="roziboldi")
    assert user.accepted_terms_at is not None


def test_register_sends_verification_email(client, db, mailoutbox):
    client.post(
        reverse("accounts:register"),
        {"username": "tasdiqsiz", "first_name": "Tasdiqsiz", "email": "tasdiqsiz@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    user = User.objects.get(username="tasdiqsiz")
    assert user.email_verified is False
    assert len(mailoutbox) == 1
    assert "tasdiqsiz@example.com" in mailoutbox[0].to


def _extract_verify_link(body):
    import re

    match = re.search(r"/hisob/email-tasdiqlash/([^/]+)/([^/\s]+)/", body)
    assert match
    return match.group(1), match.group(2)


def test_verify_email_link_marks_verified(client, db, mailoutbox):
    client.post(
        reverse("accounts:register"),
        {"username": "tasdiqla", "first_name": "Tasdiqla", "email": "tasdiqla@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    uidb64, token = _extract_verify_link(mailoutbox[0].body)

    response = client.get(reverse("accounts:verify_email", kwargs={"uidb64": uidb64, "token": token}))
    assert response.status_code == 302
    user = User.objects.get(username="tasdiqla")
    assert user.email_verified is True


def test_verify_email_rejects_invalid_token(client, db, mailoutbox):
    client.post(
        reverse("accounts:register"),
        {"username": "notogri", "first_name": "Notogri", "email": "notogri@example.com", "phone": "", "password1": "murakkab12345", "password2": "murakkab12345", "terms_accepted": "on"},
    )
    uidb64, _token = _extract_verify_link(mailoutbox[0].body)

    client.get(reverse("accounts:verify_email", kwargs={"uidb64": uidb64, "token": "yaroqsiz-token"}))
    user = User.objects.get(username="notogri")
    assert user.email_verified is False


def test_resend_verification_email(client, plain_user, mailoutbox):
    plain_user.email = "aziz@example.com"
    plain_user.save(update_fields=["email"])
    client.force_login(plain_user)
    response = client.post(reverse("accounts:resend_verification_email"))
    assert response.status_code == 302
    assert len(mailoutbox) == 1
    assert plain_user.email in mailoutbox[0].to


def test_changing_email_resets_verification(client, plain_user, mailoutbox):
    plain_user.email = "eski-email@example.com"
    plain_user.email_verified = True
    plain_user.save(update_fields=["email", "email_verified"])
    client.force_login(plain_user)

    client.post(
        reverse("accounts:profile"),
        {"first_name": plain_user.first_name, "last_name": "", "email": "yangi-email@example.com", "phone": ""},
    )
    plain_user.refresh_from_db()
    assert plain_user.email == "yangi-email@example.com"
    assert plain_user.email_verified is False
    assert len(mailoutbox) == 1
    assert "yangi-email@example.com" in mailoutbox[0].to


def test_password_reset_sends_email_and_allows_new_password(client, db, mailoutbox):
    User.objects.create_user(username="unutkan", password="eskiparol123", email="unutkan@example.com")

    response = client.post(reverse("accounts:password_reset"), {"email": "unutkan@example.com"})
    assert response.status_code == 302
    assert len(mailoutbox) == 1
    assert "unutkan@example.com" in mailoutbox[0].to

    import re

    match = re.search(r"/hisob/parol-tiklash/([^/]+)/([^/\s]+)/", mailoutbox[0].body)
    assert match
    uidb64, token = match.group(1), match.group(2)

    confirm_url = reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
    get_response = client.get(confirm_url, follow=True)
    assert get_response.status_code == 200

    post_response = client.post(
        get_response.redirect_chain[-1][0] if get_response.redirect_chain else confirm_url,
        {"new_password1": "yangiparol456", "new_password2": "yangiparol456"},
    )
    assert post_response.status_code == 302

    user = User.objects.get(username="unutkan")
    assert user.check_password("yangiparol456")


def test_resolve_contact_message_marks_resolved_for_own_pharmacy(client, staff_user, pharmacy):
    from pharmacies.models import ContactMessage

    msg = ContactMessage.objects.create(pharmacy=pharmacy, subject="s", message="m")
    client.force_login(staff_user)
    response = client.post(reverse("pharmacies:resolve_contact_message", args=[msg.id]))
    assert response.status_code == 302
    msg.refresh_from_db()
    assert msg.is_resolved is True


def test_resolve_contact_message_blocked_for_other_pharmacy(client, staff_user):
    from pharmacies.models import ContactMessage, Pharmacy

    other_pharmacy = Pharmacy.objects.create(name="Boshqa", address="X", lat=41.0, lng=69.0)
    msg = ContactMessage.objects.create(pharmacy=other_pharmacy, subject="s", message="m")
    client.force_login(staff_user)
    response = client.post(reverse("pharmacies:resolve_contact_message", args=[msg.id]))
    assert response.status_code == 404
    msg.refresh_from_db()
    assert msg.is_resolved is False


def test_profile_requires_login(client, db):
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url


def test_profile_shows_analytics(client, plain_user):
    from catalog.models import Category, Drug, Favorite, SearchQuery, Substance

    category = Category.objects.create(name_uz="Og'riq qoldiruvchi")
    substance = Substance.objects.create(name_inn="Paracetamol", category=category)
    drug = Drug.objects.create(trade_name="Panadol", substance=substance)
    Favorite.objects.create(user=plain_user, drug=drug)
    SearchQuery.objects.create(user=plain_user, query_text="panadol", result_count=1)

    client.force_login(plain_user)
    response = client.get(reverse("accounts:profile"))

    assert response.status_code == 200
    analytics = response.context["analytics"]
    assert analytics["favorite_count"] == 1
    assert analytics["search_count"] == 1
    assert analytics["top_category"] == "Og'riq qoldiruvchi"


def test_notification_badge_counts_unresolved_sent_messages_for_plain_user(client, plain_user, pharmacy):
    from pharmacies.models import ContactMessage

    ContactMessage.objects.create(sender=plain_user, subject="kutilmoqda", message="m")
    ContactMessage.objects.create(sender=plain_user, subject="hal qilingan", message="m", is_resolved=True)

    client.force_login(plain_user)
    response = client.get(reverse("catalog:home"))
    assert response.context["notification_count"] == 1
    assert response.context["notification_url"] == reverse("accounts:notifications")


def test_notification_badge_counts_unresolved_pharmacy_messages_for_staff(client, staff_user, pharmacy):
    from pharmacies.models import ContactMessage

    ContactMessage.objects.create(pharmacy=pharmacy, subject="yangi", message="m")

    client.force_login(staff_user)
    response = client.get(reverse("catalog:home"))
    assert response.context["notification_count"] == 1
    assert response.context["notification_url"] == reverse("accounts:notifications")


def test_notifications_view_shows_own_sent_messages_for_plain_user(client, plain_user, pharmacy):
    from pharmacies.models import ContactMessage

    ContactMessage.objects.create(sender=plain_user, subject="Admin uchun", message="salom", pharmacy=None)
    ContactMessage.objects.create(sender=plain_user, subject="Dorixona uchun", message="salom 2", pharmacy=pharmacy, is_resolved=True)
    other_user = User.objects.create_user(username="boshqa", password="demo12345")
    ContactMessage.objects.create(sender=other_user, subject="Boshqasiniki", message="ko'rinmasin")

    client.force_login(plain_user)
    response = client.get(reverse("accounts:notifications"))

    sent = list(response.context["sent"])
    assert len(sent) == 2
    assert {m.subject for m in sent} == {"Admin uchun", "Dorixona uchun"}


def test_notifications_view_shows_received_messages_for_staff(client, staff_user, pharmacy):
    from pharmacies.models import ContactMessage

    ContactMessage.objects.create(pharmacy=pharmacy, subject="Mijozdan", message="salom")
    other_pharmacy = Pharmacy.objects.create(name="Boshqa", address="X", lat=41.0, lng=69.0)
    ContactMessage.objects.create(pharmacy=other_pharmacy, subject="Boshqasiniki", message="ko'rinmasin")

    client.force_login(staff_user)
    response = client.get(reverse("accounts:notifications"))

    received = list(response.context["received"])
    assert len(received) == 1
    assert received[0].subject == "Mijozdan"


def test_notifications_resolve_redirects_back_to_notifications(client, staff_user, pharmacy):
    from pharmacies.models import ContactMessage

    msg = ContactMessage.objects.create(pharmacy=pharmacy, subject="s", message="m")
    client.force_login(staff_user)
    response = client.post(
        reverse("pharmacies:resolve_contact_message", args=[msg.id]),
        {"next": reverse("accounts:notifications")},
    )
    assert response.status_code == 302
    assert response.url == reverse("accounts:notifications")
    msg.refresh_from_db()
    assert msg.is_resolved is True


def test_profile_post_updates_fields(client, plain_user):
    client.force_login(plain_user)
    response = client.post(
        reverse("accounts:profile"),
        {"first_name": "Yangilangan", "last_name": "", "email": "aziz@example.com", "phone": "+998901112233"},
    )
    assert response.status_code == 302
    plain_user.refresh_from_db()
    assert plain_user.first_name == "Yangilangan"
    assert plain_user.phone == "+998901112233"


def test_pharmacy_staff_decorator_blocks_plain_user(client, plain_user):
    client.force_login(plain_user)
    response = client.get(reverse("pharmacies:staff_panel"), follow=True)
    assert response.status_code == 200
    assert response.redirect_chain[-1][0] == reverse("catalog:home")
    messages = [str(m) for m in get_messages(response.wsgi_request)]
    assert any("dorixona xodimlari uchun" in m for m in messages)


def test_pharmacy_staff_decorator_allows_staff_user(client, staff_user):
    client.force_login(staff_user)
    response = client.get(reverse("pharmacies:staff_panel"))
    assert response.status_code == 200


def test_platform_admin_decorator_blocks_plain_user(client, plain_user):
    client.force_login(plain_user)
    response = client.get(reverse("pharmacies:admin_dashboard"), follow=True)
    assert response.redirect_chain[-1][0] == reverse("catalog:home")


def test_platform_admin_decorator_allows_superuser(client, db):
    admin = User.objects.create_superuser(username="admin", password="demo12345", email="admin@example.com")
    client.force_login(admin)
    response = client.get(reverse("pharmacies:admin_dashboard"))
    assert response.status_code == 200


def test_is_pharmacy_staff_requires_pharmacy_assigned(db):
    user = User(role=UserRole.PHARMACY_STAFF)
    assert user.is_pharmacy_staff is False


def test_is_pharmacy_staff_true_with_role_and_pharmacy(staff_user):
    assert staff_user.is_pharmacy_staff is True


def test_is_platform_admin_only_for_superuser(plain_user):
    assert plain_user.is_platform_admin is False
