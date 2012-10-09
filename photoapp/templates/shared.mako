
<%inherit file="photos.mako" />

<%block name="page_header">
<ul class="nav nav-tabs">
    <li><a href="${request.route_url('my_shared')}">Shared by me</a></li>
    <li class="active"><a href="#">Shared with me</a></li>
</ul>
</%block>

<%block name="empty_list">
<p class="well">You haven't any shared photos right now.</p>
{% endblock %}
</%block>
