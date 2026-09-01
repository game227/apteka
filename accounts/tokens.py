from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Parolni tiklash tokeniga o'xshaydi, lekin email_verified holatiga
    bog'liq — email bir marta tasdiqlangach, eski havola avtomatik
    yaroqsiz bo'lib qoladi."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.email}{user.email_verified}{timestamp}"


email_verification_token = EmailVerificationTokenGenerator()
