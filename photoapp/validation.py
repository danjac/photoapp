import functools

from formencode import Invalid, Schema, validators
from formencode.variabledecode import variable_decode

from pyramid.path import DottedNameResolver


def get_form_errors(request):
    return {}


def get_form_result(request):
    return {}


def includeme(config):
    config.set_request_property(get_form_errors, 'form_errors', reify=True)
    config.set_request_property(get_form_result, 'form_result', reify=True)


def merge_form_result(obj, request):
    """Shortcut to merge the form_result dict into an object.
    """
    for k, v in request.form_result.iteritems():
        setattr(obj, k, v)
    return obj


class validate(object):
    """Decorator which validates a POST.

    If the result is successful, returns callback (if available).

    The callback must take (result, context, request) as arguments.

    Otherwise updates request.form_errors and returns original view.

    """

    def __init__(self, schema, callback=None):

        self.schema = schema
        self.callback = callback

    def __call__(self, view):

        @functools.wraps(view)
        def wrapper(context, request):

            if request.method == 'GET':
                return view(context, request)

            try:
                result = self.schema.to_python(
                    variable_decode(request.params), state=context)

                request.form_result.update(result)

                if self.callback:
                    callback = DottedNameResolver().maybe_resolve(
                        self.callback
                    )
                    return callback(context, request)

            except Invalid as e:
                request.form_errors.update(e.error_dict)
                print "errors", request.form_errors

            return view(context, request)

        return wrapper


class BaseSchema(Schema):
    allow_extra_fields = True
    filter_extra_fields = True


class EditPhotoSchema(BaseSchema):

    title = validators.String(not_empty=True)
    taglist = validators.String()
    is_public = validators.Bool()
