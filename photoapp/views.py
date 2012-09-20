import datetime
import operator
import string

import mailer
import requests
import simplejson

from pyramid.view import view_config, forbidden_view_config
from pyramid.security import remember, forget, NO_PERMISSION_REQUIRED
from pyramid.response import Response, FileResponse
from pyramid.renderers import render

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)

from webhelpers.paginate import Page

from sqlalchemy import func

from .models import (
    DBSession,
    User,
    Photo,
    Tag,
    Invite,
)

from .forms import (
    AccountForm,
    DeleteAccountForm,
    PhotoUploadForm,
    PhotoEditForm,
    PhotoShareForm,
)


@view_config(permission=NO_PERMISSION_REQUIRED,
             renderer="not_found.jinja2",
             context=HTTPNotFound)
def not_found(context, request):
    return {}


@view_config(route_name='welcome',
             permission=NO_PERMISSION_REQUIRED,
             renderer='welcome.jinja2')
def welcome(request):
    """
    Splash page. If user signed in redirects to
    home page.
    """

    if request.user:
        return HTTPFound(request.route_url('home'))

    # get random set of photos

    photos = DBSession.query(Photo).filter_by(
        is_public=True
    ).order_by(func.random()).limit(3)

    return {'photos': photos}


@view_config(route_name='home',
             renderer='photos.jinja2')
def home(request):
    """
    All the user's photos shown here.
    """

    photos = DBSession.query(Photo).filter(
        Photo.owner_id == request.user.id).order_by(
            Photo.created_at.desc())

    page = photos_page(request, photos)

    return {'page': page}


@view_config(route_name='shared',
             renderer='shared.jinja2')
def shared_photos(request):
    """
    Photos shared with the user.
    """

    page = photos_page(request, request.user.shared_photos)

    return {'page': page}


@view_config(route_name="search",
             renderer='search.jinja2')
def search(request):
    """
    Search photos by title/tags
    """

    # TBD: for Admins, include a) all photos and b) search by user name/email

    search_terms = request.params.get('search', '').split()
    search_terms = [s for s in search_terms if len(s) > 3]
    search_terms = set(search_terms[:5])

    if search_terms:
        query = [
            (Photo.title.ilike(
                "%%%s%%" % t)) | (Tag.name.ilike(t)) for t in search_terms
        ]

        query += [Photo.owner_id == request.user.id]

        query = reduce(operator.and_, query)

        photos = DBSession.query(Photo).filter(query).join(
            Photo.tags).distinct().all()

        num_photos = len(photos)
    else:
        photos = []
        num_photos = 0

    page = photos_page(request, photos, item_count=num_photos)

    return {'page': page,
            'show_search_if_empty': True}


@view_config(route_name='tags',
             renderer='json',
             xhr=True)
def get_tags(request):
    """
    Renders JSON for tagclouds.
    """

    tags = [{'text': tag.name,
             'link': request.route_url('tag', id=tag.id, name=tag.name),
             'weight': tag.frequency,
             } for tag in request.user.tags]

    return {'tags': tags}


@view_config(route_name='tag',
             renderer='photos.jinja2')
def tagged_photos(tag, request):
    """
    Show all photos matching the given tag.
    """
    page = photos_page(request, tag.photos)
    return {'page': page}


@forbidden_view_config()
def forbidden(request):
    return HTTPFound(request.route_url('welcome'))


@forbidden_view_config(xhr=True,
                       renderer='json')
def forbidden_ajax(request):
    """
    Forbidden view for AJAX requests.
    """
    return {'success': False}


@view_config(route_name='login',
             xhr=True,
             request_method="POST",
             renderer='json',
             permission=NO_PERMISSION_REQUIRED)
def login(request):
    """Allows user to sign in using Mozilla Persona.

    Returns:

        dict:

            success: True/False
            url: next URL to redirect to
    """

    data = {
        'assertion': request.POST['assertion'],
        'audience': request.host_url,
    }

    persona_url = request.registry.settings.get(
        'photoapp.persona_verification_url',
        'https://verifier.login.persona.org/verify')

    verify_response = requests.post(persona_url, data=data, verify=True)

    if verify_response.ok:

        verify_data = simplejson.loads(verify_response.content)
        if verify_data['status'] == 'okay':

            user = DBSession.query(User).filter_by(
                email=verify_data['email']
            ).first()

            if user:
                if user.is_active:
                    user.last_login_at = datetime.datetime.now()
                    response = {'success': True}

                    if user.is_complete:
                        response['url'] = request.route_url('home')
                    else:
                        request.session.flash(
                            "Please complete the rest of your details"
                        )
                        response['url'] = request.route_url('settings')

                    headers = remember(request, str(user.id))
                    request.response.headers.extend(headers)

                    return response

                return {'success': False}

            # we don't have a user
            # so let's make one

            user = User(email=verify_data['email'])

            DBSession.add(user)
            DBSession.flush()

            # go thru any invites, add photos etc

            invites = DBSession.query(Invite).filter_by(
                email=user.email,
                accepted_on=None,
            )

            for invite in invites:

                user.shared_photos.append(invite.photo)
                invite.accepted_on = None

            headers = remember(request, str(user.id))
            request.response.headers.extend(headers)

            # we need other details e.g. first name
            # so redirect to edit account form
            # in future some kind of flag needed to indicate account
            # is completed

            request.session.flash("Please complete the rest of your details")

            return {'success': False,
                    'url': request.route_url('settings')}

    return {'success': False}


@view_config(route_name="image",
             permission="view")
def image(photo, request):
    """
    Show full-size image
    """

    response = Response(content_type=photo.content_type)
    response.app_iter = photo.get_image(request.fs).read()
    return response


@view_config(route_name="download")
def download(photo, request):
    """
    Downloads photo as attachment.
    """

    response = FileResponse(photo.get_image(request.fs).path,
                            request,
                            content_type=photo.content_type)

    response.content_disposition = "attachment;filename=%s" % photo.image
    return response


@view_config(route_name="thumbnail")
def thumbnail(photo, request):
    """
    Renders the thumbnailed image of the photo.
    """

    response = Response(content_type="image/jpeg")
    response.app_iter = photo.get_thumbnail(request.fs).read()
    return response


@view_config(route_name="delete",
             permission="delete",
             request_method="POST",
             renderer='json',
             xhr=True)
def delete_photo(photo, request):
    """
    Deletes the photo.
    """

    DBSession.delete(photo)
    photo.delete_image_on_commit(request.fs)
    print "DELETING PHOTO"
    return {'success': True}


@view_config(route_name="upload",
             permission="upload",
             renderer="upload.jinja2")
def upload(request):
    """
    Upload one or more photos to the user's collection.
    """

    form = PhotoUploadForm(request)
    if form.validate():

        for image in form.images.entries:

            photo = Photo(owner=request.user,
                          title=form.title.data,
                          is_public=form.is_public.data)

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

    return {'form': form}


@view_config(route_name="edit",
             permission="edit",
             renderer="json",
             xhr=True)
def edit(photo, request):
    """
    Edit title and other photo details.
    """

    form = PhotoEditForm(request, obj=photo)

    if form.validate():

        form.populate_obj(photo)

        return {'success': True,
                'title': photo.title,
                'is_public': photo.is_public,
                'message': 'Your photo has been updated'}

    html = render(
        'edit_photo.jinja2', {
        'form': form,
        'photo': photo,
        }, request)

    return {'success': False, 'html': html}


@view_config(route_name="public",
             permission=NO_PERMISSION_REQUIRED,
             renderer="public.jinja2")
def public_photos_for_user(user, request):
    """
    Show user's public photos
    """

    photos = DBSession.query(Photo).filter_by(
        owner_id=user.id,
        is_public=True
    ).order_by(Photo.created_at.desc())

    return {'page': photos_page(request, photos), 'user': user}


@view_config(route_name="public_all",
             permission=NO_PERMISSION_REQUIRED,
             renderer="public.jinja2")
def all_public_photos(request):
    """
    Return all photos marked public for
    all users.
    """

    photos = DBSession.query(Photo).filter_by(
        is_public=True
    ).order_by(Photo.created_at.desc())

    return {'page': photos_page(request, photos), 'user': request.user}


@view_config(route_name="share",
             permission="share",
             renderer="json",
             xhr=True)
def share_photo(photo, request):
    """
    Share photo with another user.
    """

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

            send_shared_photo_email(request, photo, user, note)

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

        return {'success': True,
                'message': message}

    html = render(
        'share_photo.jinja2', {
        'form': form,
        'photo': photo,
        }, request)

    return {'success': False, 'html': html}


@view_config(route_name='about',
             renderer='about.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def about(request):
    """
    About page
    """
    return {}


@view_config(route_name='contact',
             renderer='contact.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def contact(request):
    """
    Contact details page
    """
    return {}


@view_config(route_name='settings',
             renderer='edit_account.jinja2')
def edit_account(request):
    """
    Edit user account details.
    """

    form = AccountForm(request, obj=request.user)

    if form.validate():

        form.populate_obj(request.user)
        request.session.flash("Your account settings have been saved")

        return HTTPFound(request.route_url('home'))

    return {'form': form}


@view_config(route_name='logout',
             xhr=True,
             renderer='json',
             request_method="POST")
def logout(request):
    """
    Ends the current session.
    """

    request.response.headers = forget(request)

    return {'success': True,
            'url': request.route_url('welcome')}


@view_config(route_name="delete_shared",
             permission="delete_shared",
             xhr=True,
             renderer="json")
def delete_shared(photo, request):
    """
    Removes a photo from a user's shared collection.
    Does not delete the photo itself.
    """

    request.user.shared_photos.remove(photo)
    return {'success': True}


@view_config(route_name="copy",
             permission="copy",
             xhr=True,
             renderer="json")
def copy_photo(photo, request):
    """
    Copies a shared photo over to the user's own
    collection by making a direct copy of that photo.

    The user can edit the photo before it's copied.
    """

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

        return {'success': True, 'message': message}

    html = render(
        'copy_photo.jinja2', {
        'photo': photo,
        'form': form,
        }, request)

    return {'success': False, 'html': html}


@view_config(route_name="delete_account",
             renderer="delete_account.jinja2")
def delete_account(request):

    form = DeleteAccountForm(request)
    if form.validate():

        DBSession.delete(request.user)

        for photo in request.user.photos:
            photo.delete_image_on_commit(request.fs)

        request.session.flash("Your account has been deleted")
        return HTTPFound(request.route_url("welcome"))

    return {'form': form}


def photos_page(request, photos, items_per_page=18, **kwargs):
    """
    Returns paginated photos
    """

    return Page(photos,
                int(request.params.get('page', 0)),
                items_per_page=items_per_page, **kwargs)


def send_shared_photo_email(request, photo, recipient, note):
    """
    Sends an email notifying an existing member of a photo share.
    """

    body = string.Template("""
    Hi, $first_name
    $name has shared the photo $title with you!
    Check your shared photos collection here: $url

    $note
    """).substitute(first_name=recipient.first_name,
                    name=request.user.name,
                    title=photo.title,
                    url=request.route_url('shared'),
                    note=note)

    subject = "A photo has been shared with you"

    message = mailer.Message(To=recipient.email,
                             Subject=subject,
                             Body=body)

    message.attach(photo.get_image(request.fs).path)

    request.mailer.send(message)


def send_invite_email(request, invite, note):
    """
    Sends an email to someone who is not yet a member.
    """

    body = string.Template("""
    Hi, $name has shared a photo with you!
    To see the photo, click here $url to join
    MyOwnDamnPhotos!

    $note
    """).substitute(name=request.user.name,
                    note=note,
                    url=request.route_url('welcome'))

    subject = "A photo has been shared with you"

    message = mailer.Message(To=invite.email,
                             Subject=subject,
                             Body=body)

    message.attach(invite.photo.get_image(request.fs).path)

    request.mailer.send(message)
