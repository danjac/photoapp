import cgi
import mimetypes

from wtforms import (
    TextField,
    PasswordField,
    FileField,
    HiddenField,
    SubmitField,
        )

from wtforms.validators import (
    ValidationError,
    Required,
    EqualTo,
    Email,
)

from wtforms.ext.csrf import SecureForm


class JpegRequired(object):

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        message = self.message or field.gettext("A JPEG file is required")

        if not isinstance(field.data, cgi.FieldStorage):
            raise ValidationError(message)

        type, _ = mimetypes.guess_type(field.data.filename)
        if type != "image/jpeg":
            raise ValidationError(message)


class Form(SecureForm):

    def __init__(self, request, *args, **kwargs):

        self.request = request

        if self.request.method == "POST":
            formdata = self.request.POST.copy()

        else:
            formdata = None
        
        super(Form, self).__init__(formdata, *args, **kwargs)

    def validate(self):
        if self.request.method == "GET":
            return False
        return super(Form, self).validate()

    def generate_csrf_token(self, csrf_context=None):
        return self.request.session.get_csrf_token()


class LoginForm(Form):

    email = TextField("Email address")
    password = PasswordField("Password")
    login = SubmitField("Sign in")


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
    tags = TextField("Tags")
    image = FileField("Image", validators=[JpegRequired()]) 
    submit = SubmitField("Upload")


class SendPhotoForm(Form):

    name = TextField("Name of person", validators=[Required()])
    email = TextField("Email address", validators=[Required(), Email()])
    submit = SubmitField("Send")
