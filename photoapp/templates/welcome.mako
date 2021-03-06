<%inherit file="base.mako" />

<div class="hero-unit">
    <h1>Just photos.</h1>
    <h1>Plain and simple.</h1>
    <p class="lead">Upload your photos here, keep them private, share with trusted friends and family, or show the world.</p>
    <a class="btn btn-primary btn-large" href="${request.route_url('about')}">Learn more</a>
</div>

% if photos:

<ul class="thumbnails">
    % for photo in photos:
    <li class="span4 photo">
        <a class="thumbnail" href="${request.route_url('public_all')}" title="${photo.title}">
            <img src="${request.route_url('thumbnail', id=photo.id)}" alt="${photo.title}">
        </a>
    </li>
    % endfor
</ul>

% endif
