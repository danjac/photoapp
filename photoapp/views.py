import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

from sqlalchemy import and_

from .models import User, Photo, DBSession
from .forms import LoginForm, PhotoUploadForm

@view_config(route_name='home',
             permission=NO_PERMISSION_REQUIRED,
             renderer='home.jinja2')
def home(request):

    if request.user:

        photos = DBSession.query(Photo).filter(
                    Photo.owner_id==request.user.id).order_by(
                    Photo.created_at.desc())

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

        user = DBSession.query(User).filter(
                and_(User.is_active==True, 
                     User.email==form.email.data)).first()
                                       
        if user and user.check_password(form.password.data):

            user.last_login_at = datetime.datetime.now()

            request.session.flash("Welcome back, %s" % user.first_name)

            headers = remember(request, str(user.id))
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'form' : form}


@view_config(route_name="thumbnail",
             permission="view")
def thumbnail(photo, request):
    
    response = Response(content_type="image/jpeg")
    response.app_iter = photo.load_thumbnail(request.fs)
    return response


@view_config(route_name="upload",
             permission="upload",
             renderer="upload.jinja2")
def upload(request):

    form = PhotoUploadForm(request)
    if form.validate():

        photo = Photo(owner=request.user,
                      title=form.title.data)

        photo.save_image(request.fs,
                         form.image.data.file, 
                         form.image.data.filename)

        DBSession.add(photo)

        request.session.flash("Your photo has been uploaded")
        return HTTPFound(request.route_url('home'))

    return {'form' : form}


@view_config(route_name='logout')
def logout(request):

    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
                      



