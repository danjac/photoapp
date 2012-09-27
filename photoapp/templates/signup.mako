<%inherit file="layout.mako" />
<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}">

    <legend>Sign up to get started</legend>

    ${forms.render_field(form.first_name)}
    ${forms.render_field(form.last_name)}
    ${forms.render_field(form.email)}

    ${form.submit(class="btn")}

</%forms:render_form>
