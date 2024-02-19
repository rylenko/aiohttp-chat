from typing import Any

from wtforms import validators, StringField
from wtforms import PasswordField as BasePasswordField
from wtforms import SubmitField as BaseSubmitField


class UsernameField(StringField):
	min_length = 3
	max_length = 30

	default_label = "Username"
	default_render_kw = {
		'class': "form-control",
		'minlength': min_length, 'maxlength': max_length,
		'placeholder': "Enter username of your account...",
	}

	validators = (
		validators.DataRequired(message="Username field is required."),
		validators.Length(min=min_length, max=max_length, message=(
			"Username length must not be less than"
			" %(min)d and more than %(max)d characters."
		))
	)

	def __init__(self, **kwargs: Any) -> None:
		kwargs.setdefault("label", self.default_label)
		kwargs.setdefault("render_kw", self.default_render_kw)

		super().__init__(**kwargs)


class PasswordField(BasePasswordField):
	min_length = 6
	max_length = 50

	default_label = "Password"
	default_render_kw = {
		'class': "form-control",
		'minlength': min_length, 'maxlength': max_length,
		'placeholder': "Enter password of your account...",
	}

	validators = (
		validators.DataRequired(message="Password field is required."),
		validators.Length(min=min_length, max=max_length, message=(
			"Password length must not be less than"
			" %(min)d and more than %(max)d characters."
		))
	)

	def __init__(self, **kwargs: Any) -> None:
		kwargs.setdefault("label", self.default_label)
		kwargs.setdefault("render_kw", self.default_render_kw)

		super().__init__(**kwargs)


class PasswordConfirmField(BasePasswordField):
	default_label = "Password confirm"
	default_render_kw = {
		'class': "form-control",
		'placeholder': "Confirm your password of account...",
	}

	validators = (
		validators.DataRequired(message="Password confirm field is required."),
		validators.EqualTo("password", message="Passwords must match."),
	)

	def __init__(self, **kwargs: Any) -> None:
		kwargs.setdefault("label", self.default_label)
		kwargs.setdefault("render_kw", self.default_render_kw)

		super().__init__(**kwargs)


class SubmitField(BaseSubmitField):
	default_label = ""
	default_render_kw = {'class': "btn btn-primary", 'value': "Submit"}

	def __init__(self, **kwargs: Any) -> None:
		kwargs.setdefault("label", self.default_label)
		kwargs.setdefault("render_kw", self.default_render_kw)

		super().__init__(**kwargs)
