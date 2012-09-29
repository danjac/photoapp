<%namespace file="forms.mako" name="forms" />
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <%
    import random
    descriptions = ('Plain and Simple Photo Uploads',
                    'Your Photos, For Your Eyes Only',
                    'Show Your Favorite Wallpapers Here',
                    'Private Photo Collections',)
    description = random.choice(descriptions)
    %>
    <title>My Own Damn Photos :: ${description}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${description}">
    <meta name="keywords" content="photos, uploads, private, pictures, camera, github, wallpapers, open source">
    <meta name="author" content="Dan Jacob">

    <!-- Le styles -->
    % for name in ('bootstrap_css', 'jquery_css', 'ias_css'):
        % for url in assets[name].urls():
        <link href="${url}" rel="stylesheet">
        % endfor
    % endfor

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- Le fav and touch icons -->
    <link rel="shortcut icon" href="${request.static_url('photoapp:static/favicon.ico')}">
    % if google_tracking_code:
    <script type="text/javascript">

      var _gaq = _gaq || [];
      _gaq.push(['_setAccount', '${google_tracking_code}']);
      _gaq.push(['_trackPageview']);

      (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
      })();

    </script>
    % endif
      </head>

  <body>
    <div class="navbar">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="${request.route_url('home') if request.user else request.route_url('welcome')}">My Own Damn Photos</a>
          <div class="nav-collapse">
            <ul class="nav">
            <%def name="active_tab(name)">${'class="active"' if request.matched_route and request.matched_route.name == name else ''|n} </%def>

              % if request.user:
              <li ${active_tab('home')}><a href="${request.route_url('home')}">Home</a></li>
              <li ${active_tab('shared')}><a href="${request.route_url('shared')}">Shared</a></li>
              <li ${active_tab('public')}><a href="${request.route_url('public', id=request.user.id)}">Public</a></li>
              % else:
              <li ${active_tab('public_all')}><a href="${request.route_url('public_all')}">Public photos</a></li>
              % endif
              % if has_permission('upload'):
              <li ${active_tab('upload')}><a href="${request.route_url('upload')}">Upload</a></li>
              % endif

              <li ${active_tab('about')}><a href="${request.route_url('about')}">FAQ</a></li>
              <li ${active_tab('contact')}><a href="${request.route_url('contact')}">Contact</a></li>

            </ul>
            <ul class="nav pull-right">
              % if request.user:
              <li ${active_tab('settings')}}><a href="${request.route_url('settings')}"><img src="${request.user.gravatar_url(20)}"> ${request.user.name}</a></li>
              <li><a href="${request.route_url('logout')}" class="logout">Sign out</a></li>
              % else:
              <%block name="login_button">
              <li><a href="#" class="login"><img src="https://developer.mozilla.org/files/3963/persona_sign_in_blue.png" alt="Sign in with Mozilla Persona"></a></li>
              </%block>
              % endif
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
    <noscript>
        <div class="alert alert-error">You must enable JavaScript in your browser to use this application!</div>
    </noscript>

    <div id="messages">
        % for message in request.session.pop_flash():
        <div class="alert alert-success">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            ${message}
        </div>
        % endfor
    </div>

    ${next.body()}

    % if not request.user:
    <%block name="login_form_container">
    <%forms:render_form form="${login_form}"
                        action="${request.route_url('login')}"
                        attrs="${dict(id='login-form')}">
    ${login_form.assertion}
    </%forms:render_form>
    </%block>
    % endif

    </div> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://login.persona.org/include.js"></script>
    % for name in ("jquery_js", "bootstrap_js", "ias_js", "photoapp_js"):
        % for url in assets[name].urls():
        <script src="${url}"></script>
        % endfor
    % endfor
    <script>

    PhotoApp.configure({
        csrf: '${request.session.get_csrf_token()}',
        currentUser: '${request.user.email if request.user else ''}',
    })

    PhotoApp.authenticate()

   </script>
   <%block name="scripts" />
   <%text>
    <script type="text/template" id="message-template">
        <div class="alert alert-success">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <%= message %>
        </div>
    </script>
    </%text>
  </body>
</html>
