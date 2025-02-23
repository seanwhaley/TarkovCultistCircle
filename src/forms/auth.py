from typing import Optional, Any
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    def validate_username(self, field: Any) -> Optional[bool]:
        if not field.data:
            return False
        return True

    def validate_password(self, field: Any) -> Optional[bool]:
        if not field.data:
            return False
        return True

class RegisterForm(FlaskForm):
    def validate_confirm(self, field: Any) -> Optional[bool]:
        if not field.data:
            return False
        return True
