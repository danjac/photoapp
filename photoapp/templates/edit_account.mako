<%inherit file="layout.mako" />
<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}">

    <legend>Edit your account settings</legend>

    ${forms.render_field(form.first_name)}
    ${forms.render_field(form.last_name)}
    ${forms.render_field(form.email)}

    ${form.submit(class_="btn")}

</%forms:render_form>

<ul class="nav nav-pills">

    <li><a href="${request.route_url('delete_account')}">Delete your account</a></li>

</ul>


