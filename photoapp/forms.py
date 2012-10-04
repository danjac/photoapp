import cgi
import mimetypes

from wtforms import (
    Form,
    TextField,
    TextAreaField,
    FileField,
    HiddenField,
    BooleanField,
    SubmitField,
    FieldList,
)


from wtforms.validators import (
    ValidationError,
    Required,
    Email,
)

from sqlalchemy import exists

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


class AccountForm(Form):

    first_name = TextField("First name", validators=[Required()])
    last_name = TextField("Last name", validators=[Required()])

    email = TextField("Email address",
                      validators=[Required(), Email()])

    submit = SubmitField("Save")

    def __init__(self, formdata=None, obj=None, *args, **kwargs):
        super(AccountForm, self).__init__(formdata, obj, *args, **kwargs)
        self.user = obj

    def validate_email(self, field):

        where = (User.email == field.data)
        if self.user:
            where = where & ~(User.email == self.user.email)

        if DBSession.query(exists().where(where)).scalar():
            raise ValidationError("This email address is already taken")


class DeleteAccountForm(Form):
    pass


class PhotoUploadForm(Form):

    title = TextField("Title", validators=[Required()])
    taglist = TextField("Tags")
    is_public = BooleanField("Make this photo public")

    images = FieldList(
        FileField(validators=[ImageRequired()]),
        min_entries=1,
        max_entries=3
    )

    submit = SubmitField("Upload")


class PhotoEditForm(Form):

    title = TextField("Title", validators=[Required()])
    taglist = TextField("Tags")
    is_public = BooleanField("Make this photo public")
    submit = SubmitField("Update")


class PhotoShareForm(Form):

    note = TextAreaField("Message")

    emails = FieldList(
        TextField(validators=[Required(), Email()]),
        min_entries=1
    )

    submit = SubmitField("Share")


class LoginForm(Form):

    assertion = HiddenField(validators=[Required()])


class DeletePhotoForm(Form):
    pass
