
<%inherit file="photos.mako" />

<%block name="page_header">

% if request.user or user:
<ul class="nav nav-tabs">
    <li${' class="active"' if request.matched_route.name == 'public' else '' | n }><a href="${request.route_url('public', id=user.id )}">
    % if user == request.user:
    My photos
    % else:
    ${user.first_name}'s photos
    % endif
    </a></li>
    <li${' class="active"' if request.matched_route.name == 'public_all' else '' | n }><a href="${request.route_url('public_all')}">Everyone's photos</a></li>
</ul>
% else:

<p class="lead">
    These are photos members have chosen to make public, so everyone can see them.
</p>

% endif
</%block>

<%block name="empty_list">
<div class="row">
    <div class="span12">There are no public photos here yet.</div>
</div>
</%block>
