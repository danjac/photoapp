import cgi
import mimetypes
import string

from wtforms import (
    TextField,
    TextAreaField,
    PasswordField,
    FileField,
    HiddenField,
    SubmitField,
    FieldList,
        )

from wtforms.validators import (
    ValidationError,
    Required,
    EqualTo,
    Email,
)

from wtforms.ext.csrf import SecureForm

from sqlalchemy import exists, and_, not_

from .models import User, DBSession


class ImageRequired(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        message = self.message or field.gettext(
                "A PNG or JPEG file is required")

        if not isinstance(field.data, cgi.FieldStorage):
            raise ValidationError(message)

        type, _ = mimetypes.guess_type(field.data.filename)

        if type not in ("image/jpeg", "image/png"):
            raise ValidationError(message)


class Form(SecureForm):

    def __init__(self, request, *args, **kwargs):

        self.request = request

        if self.request.method == "POST":
            formdata = self.request.POST

        else:
            formdata = None
        
        super(Form, self).__init__(formdata, *args, **kwargs)

    def validate(self, *args, **kwargs):

        if self.request.method == "GET":
            return False
        return super(Form, self).validate(*args, **kwargs)

    def generate_csrf_token(self, csrf_context=None):
        return self.request.session.get_csrf_token()


class LoginForm(Form):

    email = TextField("Email address")
    password = PasswordField("Password")
    login = SubmitField("Sign in")


class AccountForm(Form):

    invite = HiddenField()

    first_name = TextField("First name", validators=[Required()])
    last_name = TextField("Last name", validators=[Required()])

    email = TextField("Email address", 
                      validators=[Required(), Email()])

    password = PasswordField("New password", validators=[Required()])

    password_again = PasswordField("Repeat password", 
                        validators=[EqualTo('password')])

    
    submit = SubmitField("Save")


class EditAccountForm(AccountForm):

    def __init__(self, *args, **kwargs):

        super(EditAccountForm, self).__init__(*args, **kwargs)
        try:
            obj = kwargs['obj']
        except KeyError:
            raise ValueError("obj is a required argument")

        self.current_email = obj.email

    def validate_email(self, field):
        """
        When latest version of wtforms comes out use extra_validators
        instead to get current user email.
        """
        if DBSession.query(exists().where(
            and_(User.email==field.data,
                 not_(User.email==self.current_email)))).scalar():
            raise ValidationError("This email address is already taken")


class SignupForm(AccountForm):

    submit = SubmitField("Sign up")

    def validate_email(self, field):

        if DBSession.query(exists().where(User.email==field.data)).scalar():
            raise ValidationError("This email address is already taken")


class ForgotPasswordForm(Form):

    email = TextField("Email address", validators=[Required(), Email()])
    submit = SubmitField("Go")


class ChangePasswordForm(Form):

    key = HiddenField()

    password = PasswordField("New password", validators=[Required()])

    password_again = PasswordField("Repeat password", 
                        validators=[EqualTo('password')])

    submit = SubmitField("Change")


class PhotoUploadForm(Form):

    title = TextField("Title", validators=[Required()])
    taglist = TextField("Tags")

    images = FieldList(
                FileField(validators=[ImageRequired()]),
                min_entries=1, max_entries=3)

    submit = SubmitField("Upload")


class PhotoEditForm(Form):

    title = TextField("Title", validators=[Required()])
    taglist = TextField("Tags")
    submit = SubmitField("Update")


class PhotoShareForm(Form):

    note = TextAreaField("Message")

    emails = FieldList(
                TextField(validators=[Required(), 
                                      Email()]), min_entries=1)

    submit = SubmitField("Share")


class SendPhotoForm(Form):

    name = TextField("Name of person", validators=[Required()])
    note = TextAreaField("Message")
    email = TextField("Email address", validators=[Required(), Email()])
    submit = SubmitField("Send")
