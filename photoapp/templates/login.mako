<%inherit file="layout.mako" />

<%block name="login_button" />
<%block name="login_form_container" />

% if signup_form:

<%forms:render_form(signup_form, action="${request.route_url('signup'))}">

    <legend>Please complete the form below to get started</legend>
    ${forms.render_field(signup_form.first_name)}
    ${forms.render_field(signup_form.last_name)}
    ${forms.render_field(signup_form.email)}

    ${signup_form.submit(class_="btn")}

<%/forms:render_form>

% else:
<p class="well">There appears to be a problem signing in. Please try again by clicking <a href="#" class="login">here</a>.</p>
% endif

