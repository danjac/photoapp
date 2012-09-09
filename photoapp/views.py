import datetime

import mailer

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response, FileResponse
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from sqlalchemy import and_, or_

from webhelpers.paginate import Page

from .models import (
    DBSession,
    User, 
    Photo, 
    Tag, 
    Invite,
    )

from .forms import (
    LoginForm, 
    SignupForm,
    EditAccountForm,
    PhotoUploadForm,
    PhotoEditForm,
    PhotoShareForm,
    SendPhotoForm,
    ForgotPasswordForm,
    ChangePasswordForm,
    )


@view_config(route_name='welcome',
             permission=NO_PERMISSION_REQUIRED,
             renderer='welcome.jinja2')
def welcome(request):
    
    if request.user:
        return HTTPFound(request.route_url('home'))

    return {}


@view_config(route_name='home',
             renderer='photos.jinja2')
def home(request):

    photos = DBSession.query(Photo).filter(
                Photo.owner_id==request.user.id).order_by(
                Photo.created_at.desc())
    
    page = photos_page(request, photos)

    return {'page' : page}


@view_config(route_name='shared',
             renderer='shared.jinja2')
def shared_photos(request):

    page = photos_page(request, request.user.shared_photos)

    return {'page' : page}


@view_config(route_name="search",
             renderer='search.jinja2')
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

    page = photos_page(request, photos, item_count=num_photos)

    return {'page' : page, 
            'show_search_if_empty' : True}


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

    page = photos_page(request, tag.photos)
    return {'page' : page}


@forbidden_view_config(xhr=True,
                       renderer='json')
def forbidden_ajax(request):
    return {'success' : False}


@view_config(route_name='login',
             permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
@forbidden_view_config(renderer='login.jinja2')
def login(request):
    
    form = LoginForm(request, next=request.url)

    if form.validate():

        user = User.authenticate(form.email.data, form.password.data)
        if user:
            user.last_login_at = datetime.datetime.now()

            request.session.flash("Welcome back, %s" % user.first_name)

            headers = remember(request, str(user.id))
            default_redirect = request.route_url('home')

            if request.matched_route.name == "login":
                redirect = default_redirect
            else:
                redirect = form.next.data or default_redirect

            return HTTPFound(redirect, headers=headers)


    return {'form' : form}


@view_config(route_name='signup',
             permission=NO_PERMISSION_REQUIRED,
             renderer='signup.jinja2')
def signup(request):

    invite_key = request.params.get('invite')

    if invite_key:
        invite = DBSession.query(Invite).filter_by(
            accepted_on=None,
            key=invite_key).first()

        form = SignupForm(request, 
                          invite=invite_key,
                          email=invite.email)

    else:
        form = SignupForm(request)
        invite = None

    if form.validate():

        user = User()
        form.populate_obj(user)

        DBSession.add(user)
        DBSession.flush()

        if invite:
            user.shared_photos.append(invite.photo)
            invite.accepted_on = datetime.datetime.now()

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

            send_forgot_password_email(request, user)

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
    
    response = Response(content_type=photo.content_type)
    response.app_iter = photo.get_image(request.fs).read()
    return response


@view_config(route_name="download",
             permission="view")
def download(photo, request):

    response = FileResponse(photo.get_image(request.fs).path,
                            request,
                            content_type=photo.content_type)

    response.content_disposition = "attachment;filename=%s" % photo.image
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

        send_photo_attachment_email(
            request, 
            photo, 
            form.name.data, 
            form.email.data,
            form.note.data,
                )

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

        for image in form.images.entries:

            photo = Photo(owner=request.user,
                          title=form.title.data)

            photo.save_image(request.fs,
                             image.data.file, 
                             image.data.filename)
            
            photo.taglist = form.taglist.data

            DBSession.add(photo)

        if len(form.images.entries) == 1:
            message = "Your photo has been uploaded"
        else:
            message = "Your photos have been uploaded"

        request.session.flash(message)
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
                     

@view_config(route_name="share",
             permission="share",
             renderer="json",
             xhr=True)
def share_photo(photo, request):

    form = PhotoShareForm(request)

    if form.validate():

        note = (form.note.data or '').strip()

        emails = set(item.data.lower() for item in form.emails.entries)

        if request.user.email in emails:
            emails.remove(request.user.email)

        users = DBSession.query(User).filter(User.email.in_(emails))
        emails_for_invites = set(emails)

        for user in users:

            user.shared_photos.append(photo)
            emails_for_invites.remove(user.email)

            send_shared_photo_notification_email(request, photo, user, note)
            
        for email in emails_for_invites:

            invite = Invite(sender=request.user,
                            photo=photo,
                            email=email)


            DBSession.add(invite)
            DBSession.flush()

            send_invite_email(request, invite, note)

        if len(emails) == 1:
            message = "You have shared this photo with one person"
        else:
            message = "You have shared this photo with %d people" % len(emails)

        return {'success' : True, 
                'message' : message}

    html = render('share_photo.jinja2', {
        'form' : form,
        'photo' : photo,
        }, request)

    return {'success' : False, 'html' : html}


@view_config(route_name='about',
             renderer='about.jinja2', 
             permission=NO_PERMISSION_REQUIRED)
def about(request):
    return {}


@view_config(route_name='contact',
             renderer='contact.jinja2', 
             permission=NO_PERMISSION_REQUIRED)
def contact(request):
    return {}


@view_config(route_name='settings',
             renderer='edit_account.jinja2')
def edit_account(request):

    form = EditAccountForm(request, obj=request.user)

    if form.validate():

        form.populate_obj(request.user)
        request.session.flash("Your account settings have been saved")

        return HTTPFound(request.route_url('home'))

    return {'form' : form}


@view_config(route_name='logout')
def logout(request):

    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)
 

@view_config(route_name="delete_shared",
             permission="delete_shared",
             xhr=True,
             renderer="json")
def delete_shared(photo, request):
    request.user.shared_photos.remove(photo)
    return {'success' : True}


@view_config(route_name="copy",
             permission="copy",
             xhr=True,
             renderer="json")
def copy_photo(photo, request):

    form = PhotoEditForm(request,
                         title=photo.title,
                         taglist=photo.taglist)
                      
    if form.validate():

        new_photo = Photo(owner=request.user,
                          title=form.title.data)
                          
        new_photo.taglist = form.taglist.data

        new_photo.save_image(request.fs,
                             photo.get_image(request.fs).open('rb'),
                             photo.image)

        DBSession.add(new_photo)

        request.user.shared_photos.remove(photo)
        
        message = "Photo has been added to your collection"

        return {'success' : True, 'message' : message}

    html = render('copy_photo.jinja2', {
        'photo' : photo,
        'form' : form,
        }, request)

    return {'success' : False, 'html' : html}


def photos_page(request, photos, items_per_page=18, **kwargs):

    return Page(photos, 
                int(request.params.get('page', 0)), 
                items_per_page=items_per_page, **kwargs)

# Emails

def send_forgot_password_email(request, user):

    body = """
    Hi, {first_name}

    Please go here : {url} to change your password.

    Thanks!
    """.format(
        first_name=user.first_name, 
        url=request.route_url('change_pass', 
                              _query={'key' : user.key})
    )

    message = mailer.Message(To=user.email,
                             Subject="Change your password!",
                             Body=body)


    request.mailer.send(message)


def send_photo_attachment_email(request, photo, 
        recipient_name, recipient_email, note):

    body = """ 
    Hi {recipient_name},
    {sender_name} sent you a photo! 
    {note}
    """.format(sender_name=request.user.first_name,
               recipient_name=recipient_name,
               note=note)

    message = mailer.Message(To=recipient_email,
                             Subject=photo.title,
                             Body=body)

    message.attach(photo.get_image(request.fs).path)

    request.mailer.send(message)


def send_shared_photo_notification_email(request, photo, recipient, note):

    body = """
    Hi, {first_name}
    {name} has shared the photo {title} with you!
    Check your shared photos collection here: {url}
    {note}
    """.format(
        first_name=recipient.first_name,
        name=request.user.name,
        title=photo.title,
        url=request.route_url('shared'),
        note=note)

    subject = "A photo has been shared with you"

    message = mailer.Message(To=recipient.email,
                             Subject=subject,
                             Body=body)
                             
    request.mailer.send(message)


def send_invite_email(request, invite, note):

    url = request.route_url('signup', _query={'invite' : invite.key})

    body = """
    Hi, {name} has shared a photo with you!
    To see the photo, click here {url} to join 
    MyOwnDamnPhotos!
    {note}
    """.format(name=request.user.name, 
               note=note,
               url=url)


    subject = "A photo has been shared with you"

    message = mailer.Message(To=invite.email,
                             Subject=subject,
                             Body=body)
                             

    request.mailer.send(message)


