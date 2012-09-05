import random
import datetime

import mailer

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from sqlalchemy import and_, or_

from webhelpers.paginate import Page

from .models import User, Photo, Tag, DBSession

from .forms import (
    LoginForm, 
    SignupForm,
    PhotoUploadForm,
    PhotoEditForm,
    SendPhotoForm,
    ForgotPasswordForm,
    ChangePasswordForm
    )


@view_config(route_name='home',
             renderer='photos.jinja2')
def home(request):

    photos = DBSession.query(Photo).filter(
                Photo.owner_id==request.user.id).order_by(
                Photo.created_at.desc())
    
    page = Page(photos, int(request.params.get('page', 0)), items_per_page=18)

    return {'page' : page}


@view_config(route_name="search",
             renderer='photos.jinja2')
def search(request):

    search_terms = request.params.get('search', '').split()
    search_terms = set(s for s in search_terms if len(s) > 3)

    if search_terms:
        q = [(or_(Photo.title.ilike("%%%s%%" % q), 
                  Tag.name.ilike(q))) for q in search_terms]

        q = reduce(and_, q)

        photos = DBSession.query(Photo).filter(q).join(
                    Photo.tags).distinct().all()

        num_photos = len(photos)
    else:
        photos = []
        num_photos = 0

    page = Page(photos, 
                int(request.params.get('page', 0)), 
                item_count=num_photos,
                items_per_page=18)

    return {'page' : page}


@view_config(route_name='tags',
             renderer='json',
             xhr=True)
def tags(request):

    tags = [{'text' : tag.name,
             'link' : request.route_url('tag', id=tag.id, name=tag.name),
             'weight' : tag.frequency,
             } for tag in request.user.tags]

    return {'tags' : tags}


@view_config(route_name='tag',
             renderer='photos.jinja2')
def tagged_photos(tag, request):

    page = Page(tag.photos, 
                int(request.params.get('page', 0)), 
                items_per_page=18)

    return {'page' : page}


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


@view_config(route_name='signup',
             permission=NO_PERMISSION_REQUIRED,
             renderer='signup.jinja2')
def signup(request):

    form = SignupForm(request)

    if form.validate():

        user = User()
        form.populate_obj(user)

        DBSession.add(user)
        DBSession.flush()

        request.session.flash("Welcome, %s" % user.first_name)
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

            user.reset_key()

            body = """
            Hi, {first_name}

            Please go here : {url} to change your password.

            Thanks!
            """.format(
                first_name=user.first_name, 
                url=request.route_url('change_pass', 
                                      _query={'key' : user.key})
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
            user = DBSession.query(User).filter_by(key=key).first()
    
    if user is None:
        raise HTTPForbidden()

    form = ChangePasswordForm(request, key=key)
    if form.validate():
        user.password = form.password.data
        user.key = None
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
             permission="delete",
             request_method="POST",
             renderer='json',
             xhr=True)
def delete_photo(photo, request):

    DBSession.delete(photo)
    photo.delete_image_on_commit(request.fs)
    return {'success' : True}

             
@view_config(route_name="send",
             permission="view",
             renderer="json",
             xhr=True)
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

        message = "You have emailed the photo %s to %s" % (
                photo.title, 
                form.email.data
                )

        return {'success' : True, 'message' : message}

    html = render('send_photo.jinja2', {
        'photo' : photo,
        'form' : form,
        }, request)

    return {'success' : False, 'html' : html}


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

        photo.taglist = form.taglist.data

        request.session.flash("Your photo has been uploaded")
        return HTTPFound(request.route_url('home'))

    return {'form' : form}


@view_config(route_name="edit",
             permission="edit",
             renderer="json",
             xhr=True)
def edit(photo, request):

    form = PhotoEditForm(request, obj=photo)

    if form.validate():

        form.populate_obj(photo)

        return {'success' : True, 
                'title' : photo.title,
                'message' : 'Your photo has been updated'}

    html = render('edit_photo.jinja2', {
        'form' : form,
        'photo' : photo,
        }, request)


    return {'success' : False, 'html' : html}


@view_config(route_name='logout')
def logout(request):

    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
                      



