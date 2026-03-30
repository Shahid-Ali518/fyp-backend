# --- METHOD LEVEL SECURITY HELPER ---
from typing import List

from fastapi import Depends, HTTPException
from starlette import status

from core.security import get_current_user
from models import User


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role.value not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user

# Global instances for reuse
admin_only = RoleChecker(["ADMIN"])
any_user = RoleChecker(["ADMIN", "USER"])
user_only = RoleChecker(["USER"])