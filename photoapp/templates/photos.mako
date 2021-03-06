<%inherit file="base.mako" />
<%namespace file="pagination.mako" name="pagination" />

<div id="photo-modal" class="modal hide fade"></div>

<%text>
<script type="text/template" id="tag-cloud-template">
    <div class="well" id="tag-cloud" style="height:250px;"></div>
</script>

<script type="text/template" id="share-field-template">
<dd>
    <div class="control-group">
        <div class="controls">
            <input type="text" name="emails-<%= numItems %>" />
            <a href="#" class="remove-share-email"><i class="icon-remove"></i></a>
        </div>
    </div>
</dd>
</script>

<script type="text/template" id="photo-modal-template">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3><%= title %></h3>
        <% if (owner) { %>
        <h4>owned by <a href="<%= ownerURL %>"><%= owner %></a></h4>
        <% } %>
        <div class="permalink-container permalink-container-is-public hide">
            <input type="text" class="permalink span4" value="<%= imageURL %>">
            <a class="close-permalink-btn" href="#"><i class="icon-remove"></i></a>
        </div>
        <div class="permalink-container permalink-container-is-private alert alert-warning hide">
            <button type="button" class="close close-permalink-btn">&times;</button>
            You can only link to a photo you have made public. Click 'Edit' and select the 'Make this photo public' checkbox.
        </div>
    </div>
    <div class="modal-body" id="photo-modal-body">
        <div class="messages hide"></div>
        <div class="photo-load-progress progress progress-striped active"><div class="bar" style="width:0%;"></div></div>
        <div id="photo-modal-load"></div>
        <p id="photo-modal-content">
            <a class="photo-image hide" target="_blank" href="<%= imageURL %>">
                <img src="<%= thumbnailURL %>" height="<%= height %>" width="<%= width %>" alt="<%= title %>">
            </a>
        </p>
    </div>
    <div class="modal-footer hide" id="photo-modal-footer">
        <div class="buttons">
            <a href="javascript:void(0);" class="btn permalink-btn"><i class="icon-asterisk"></i> Permalink</a>
            <a href="<%= downloadURL %>" class="btn download-btn"><i class="icon-download"></i> Download</a>
            <a href="javascript:void(0);" class="btn share-btn"><i class="icon-share"></i> Share</a>
            <a href="javascript:void(0);" class="btn edit-btn"><i class="icon-pencil"></i> Edit</a>
            <a href="javascript:void(0);" class="btn delete-btn"><i class="icon-trash"></i> Delete</a>
            <a href="javascript:void(0);" class="btn copy-btn"><i class="icon-plus"></i> Add to my collection</a>
            <a href="javascript:void(0);" class="btn delete-shared-btn"><i class="icon-trash"></i> Delete</a>
        </div>
    </div>
</script>
</%text>

<%block name="page_header">
% if page.item_count or show_search_if_empty:
<div class="btn-group">
    <button class="btn btn-large btn-block btn-primary" href="#" type="button" id="search-btn"><i class="icon-search icon-white"></i></button>
</div>

<div id="search-box" class="hide">
    <form class="form-search" method="GET" action="${request.route_url('search')}">
        <div class="btn-group">
            <input type="search" style="font-size:large; font-weight:bold;" name="search" value="${request.params.get('search', '')}" placeholder="Search for...." class="span12">
        </div>
    </form>
</div>
% endif
</%block>

% if page.item_count:
<ul class="thumbnails">
% for photo in page.items:
    <li class="span4 photo">
        <a
           data-image-url="${request.route_url('image', id=photo.id)}"
           data-thumbnail-url="${request.route_url('thumbnail', id=photo.id)}"
           data-download-url="${request.route_url('download', id=photo.id)}"
           data-photo-id="${photo.id}"
           data-width="${photo.width}"
           data-height="${photo.height}"
           data-title="${photo.title}"
           % if photo.is_public:
           data-is-public="1"
           % endif
           % if request.user is None or request.user.id != photo.owner_id:
           data-owner="${photo.owner.name}"
           data-owner-url="${request.route_url('public', id=photo.owner_id)}"
           % endif
           % if has_permission('edit', photo):
           data-edit-url="${request.route_url('edit', id=photo.id)}"
           % endif
           % if has_permission('share', photo):
           data-share-url="${request.route_url('share', id=photo.id)}"
           % endif
           % if has_permission('delete', photo):
           data-delete-url="${request.route_url('delete', id=photo.id)}"
           % endif
           % if has_permission('delete_shared', photo):
           data-delete-shared-url="${request.route_url('delete_shared', id=photo.id)}"
           % endif
           % if has_permission('copy', photo):
           data-copy-url="${request.route_url('copy', id=photo.id)}"
           % endif
            href="${request.route_url('image', id=photo.id)}" target="_blank" class="thumbnail">
            <img src="${request.route_url('thumbnail', id=photo.id)}" title="${photo.title}" alt="${photo.title}">
        </a>
    </li>
% endfor
</ul>
<div id="loader" class="hide"><img src="${request.static_url('photoapp:static/ias/loader.gif')}"></div>
% else:
<%block name="empty_list">
<div class="row">
    <div class="span12">You don't appear to have any photos at the moment. Go <a href="${request.route_url('upload')}">here</a> to upload some photos!</div>
</div>
</%block>
% endif


${pagination.render_page_links(page)}


<%block name="scripts">
<script>
    new PhotoApp.PhotosPage('${request.route_url('tags')}');
</script>
</%block>
