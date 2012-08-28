import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from .models import User, Photo
from .forms import LoginForm, PhotoUploadForm

@view_config(route_name='home',
             permission=NO_PERMISSION_REQUIRED,
             renderer='home.jinja2')
def home(request):

    if request.user:
        photos = Photo.objects.filter(
                    owner=request.user).order_by('-created_at')
    else:
        photos = []

    return {'login_form' : LoginForm(request),
            'photos' : photos }


@view_config(route_name='login',
             permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
@forbidden_view_config(renderer='login.jinja2')
def login(request):
    
    form = LoginForm(request)

    if form.validate():
        user = User.objects.authenticate(form.email.data, 
                                         form.password.data)
        if user:

            user.last_login_at = datetime.datetime.now()
            user.save()

            request.session.flash("Welcome back, %s" % user.first_name)

            headers = remember(request, str(user.id))
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'form' : form}


@view_config(route_name="thumbnail",
             permission="view")
def thumbnail(photo, request):
    
    print "THUMBNAIL"
    response = Response(content_type="image/jpeg")
    response.app_iter = photo.image.thumbnail.read()
    return response

@view_config(route_name="upload",
             permission="upload",
             renderer="upload.jinja2")
def upload(request):


    print "USER", request.user

    print request.POST
    form = PhotoUploadForm(request)
    if form.validate():

        photo = Photo(owner=request.user,
                      title=form.title.data)

        photo.image.put(form.image.data.file, 
                        filename=form.image.data.filename)

        photo.save()

        request.session.flash("Your photo has been uploaded")
        return HTTPFound(request.route_url('home'))
    else:
        print form.errors

    return {'form' : form}


@view_config(route_name='logout')
def logout(request):

    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
                      



