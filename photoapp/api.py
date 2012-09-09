from cornice import Service

from .resources import Root
from .models import Photo, DBSession

upload = Service(name="upload",
                 path="/api/upload",
                 description="PhotoApp API",
                 factory=Root)


@upload.put()
def upload_photo(request):

    uploaded_file = request.params.get('uploaded_file')
    tags = request.params.get('tags')
    title = request.params.get('title')

    # TBD: validate uploaded file

    photo = Photo(owner=request.user,
                  title=title or uploaded_file.filename)

    photo.save_image(request.fs,
                     uploaded_file.file,
                     uploaded_file.filename)

    DBSession.add(photo)

    photo.taglist = tags

    return {"success": True}
