from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User Model for the paper_ai system.
    Supports role-based access control with roles: Admin, Process Engineer, Operator.
    """
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        PROCESS_ENGINEER = 'PROCESS_ENGINEER', _('Process Engineer')
        OPERATOR = 'OPERATOR', _('Operator')

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.OPERATOR,
        help_text=_('Designates the role of the user inside the paper_ai platform.')
    )

    @property
    def is_admin(self) -> bool:
        return self.role == self.Roles.ADMIN or self.is_superuser

    @property
    def is_process_engineer(self) -> bool:
        return self.role == self.Roles.PROCESS_ENGINEER

    @property
    def is_operator(self) -> bool:
        return self.role == self.Roles.OPERATOR

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
