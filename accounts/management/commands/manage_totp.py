from urllib.parse import parse_qs, urlparse

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_otp.plugins.otp_totp.models import TOTPDevice


class Command(BaseCommand):
    help = "Provision or revoke a staff member's authenticator device."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--revoke", action="store_true", help="Revoke all authenticator devices for this user.")

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist as exc:
            raise CommandError("No staff account has that username.") from exc

        devices = TOTPDevice.objects.devices_for_user(user)
        if options["revoke"]:
            deleted, _ = devices.delete()
            self.stdout.write(self.style.SUCCESS(f"Revoked {deleted} authenticator device(s)."))
            return

        if devices.exists():
            raise CommandError("An authenticator device already exists. Revoke it before provisioning a replacement.")

        device = TOTPDevice.objects.create(user=user, name="EPRMS authenticator", confirmed=True)
        setup_key = parse_qs(urlparse(device.config_url).query).get("secret", [""])[0]
        self.stdout.write(self.style.WARNING(
            "Treat this setup key as a password. Deliver it only through a verified private channel."
        ))
        self.stdout.write(f"Account: {user.username}")
        self.stdout.write("Issuer: EPRMS")
        self.stdout.write(f"Setup key: {setup_key}")
