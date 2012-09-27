<%inherit file="photos.mako" />

<%block name="empty_list">
<div class="row">
    <div class="span12">Sorry, no results found for your search. Please try again!</div>
</div>
</%block>

${next.body()}

