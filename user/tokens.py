from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils import six

class PasswordResetToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)

        return "test"
        # return (
        #     six.text_type(user.pk) + six.text_type(timestamp) +
        #     six.text_type(login_timestamp)
        # )

password_reset_token=PasswordResetToken()



class AccountVerificationToken(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)

        return "test"
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(login_timestamp)
        )








account_verification_token=AccountVerificationToken()