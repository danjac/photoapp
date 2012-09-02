import datetime
import mailer

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from sqlalchemy import and_
from webhelpers.paginate import Page

from .models import User, Photo, DBSession

from .forms import (
    LoginForm, 
    PhotoUploadForm,
    SendPhotoForm,
    ForgotPasswordForm,
    ChangePasswordForm
    )


@view_config(route_name='home',
             permission=NO_PERMISSION_REQUIRED,
             renderer='home.jinja2')
def home(request):

    if request.user:

        photos = DBSession.query(Photo).filter(
                    Photo.owner_id==request.user.id).order_by(
                    Photo.created_at.desc())
        
        page = Page(photos, 
                    int(request.params.get('page', 0)), 
                    items_per_page=6)

        return {'page' : page}

    return {'login_form' : LoginForm(request)}



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


@view_config(route_name='forgot_pass',
             permission=NO_PERMISSION_REQUIRED,
             renderer='forgot_password.jinja2')
def forgot_password(request):

    form = ForgotPasswordForm(request)

    if form.validate():
        user = DBSession.query(User).filter_by(email=form.email.data).first()
        if user:
            # for now we'll just use ID. Obviously in future we'll go with
            # a one-time random field.
            #key = request.session['key'] = str(user.id)
            key  = str(user.id)
            #ForgotPasswordEmail(user, key, request).send()

            body = """
            Hi, {first_name}

            Please go here : {url} to change your password.

            Thanks!
            """.format(
                first_name=user.first_name, 
                url=request.route_url('change_pass', _query={'key' : key})
            )

            msg = mailer.Message(To=user.email,
                                 Subject="Change your password!",
                                 Body=body)

            request.mailer.send(msg)

            request.session.flash(
                "Please check your inbox, we have emailed "
                "you instructions to recover your password")

            return HTTPFound(request.route_url('home'))

    return {'form' : form}


@view_config(route_name='change_pass',
             permission=NO_PERMISSION_REQUIRED,
             renderer='change_password.jinja2')
def change_password(request):

    user = request.user
    key = None

    if user is None:
        key = request.params.get('key', None)
        if key:
        #if key and key == request.params.get('key'):
            user = DBSession.query(User).get(key)
    
    if user is None:
        raise HTTPForbidden()

    form = ChangePasswordForm(request, key=key)
    if form.validate():
        user.password = form.password.data
        request.session.flash("Please sign in again with your new password")
        return HTTPFound(request.route_url('login'))

    return {'form' : form}


@view_config(route_name="image",
             permission="view")
def image(photo, request):
    """
    Show full-size image
    """
    
    response = Response(content_type="image/jpeg")
    response.app_iter = photo.get_image(request.fs).read()
    return response



@view_config(route_name="thumbnail",
             permission="view")
def thumbnail(photo, request):
    
    response = Response(content_type="image/jpeg")
    response.app_iter = photo.get_thumbnail(request.fs).read()
    return response


@view_config(route_name="delete",
             permission="delete")
def delete_photo(photo, request):

    DBSession.delete(photo)
    request.session.flash("You have deleted the photo %s" % photo.title)
    return HTTPFound(request.route_url("home"))

             
@view_config(route_name="send",
             permission="view",
             renderer="send_photo.jinja2")
def send_photo(photo, request):

    form = SendPhotoForm(request)

    if form.validate():

        body = """ 
        Hi {recipient_name},
        {sender_name} sent you a photo!
        """.format(sender_name=request.user.first_name,
                   recipient_name=form.name.data)

        
        message = mailer.Message(To=form.email.data,
                                 From=request.user.email,
                                 Subject=photo.title,
                                 Body=body)

        message.attach(photo.get_image(request.fs).path)

        request.mailer.send(message)

        request.session.flash(
            "You sent %s the photo %s"  % (form.name.data, photo.title))

        return HTTPFound(request.route_url('home'))

    return {'photo' : photo, 'form' : form}        
        

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
                      



