from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.db import transaction


ROLE_SPECS = [
    {
        "role_name": "超级管理员",
        "username": "super_admin",
        "password": "admin@123",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "role_name": "管理员",
        "username": "admin",
        "password": "admin123",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "role_name": "访客",
        "username": "guest",
        "password": "guest123",
        "is_staff": False,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = "Create initial login accounts: super_admin/admin/guest."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Reset passwords even if user exists.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset_passwords = bool(options["reset_passwords"])

        # Create groups
        groups = {}
        for spec in ROLE_SPECS:
            group, _ = Group.objects.get_or_create(name=spec["role_name"])
            groups[spec["role_name"]] = group

        # Assign permissions for robots app (if installed)
        robot_permissions = Permission.objects.filter(content_type__app_label="robots")
        if robot_permissions.exists():
            perms_by_codename = {p.codename: p for p in robot_permissions}
            admin_perms = []
            guest_perms = []
            for codename, perm in perms_by_codename.items():
                if codename.startswith("view_"):
                    guest_perms.append(perm)
                    admin_perms.append(perm)
                if codename.startswith(("add_", "change_", "delete_")):
                    admin_perms.append(perm)

            groups["管理员"].permissions.set(admin_perms)
            groups["访客"].permissions.set(guest_perms)

        for spec in ROLE_SPECS:
            user, created = User.objects.get_or_create(username=spec["username"])
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            if created or reset_passwords:
                user.set_password(spec["password"])
            user.save()

            # Superuser doesn't need group perms, but still attach role group for clarity
            role_group = groups[spec["role_name"]]
            user.groups.add(role_group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"OK: {spec['role_name']} -> {spec['username']} (password {'reset' if reset_passwords else 'set if new'})"
                )
            )
