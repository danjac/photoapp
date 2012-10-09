<%inherit file="base.mako" />
<%namespace file="forms.mako" name="forms" />

<%forms:form form="${form}"
             legend="Edit your account settings">

    ${forms.field(form.first_name)}
    ${forms.field(form.last_name)}
    ${forms.field(form.email)}

    ${form.submit(class_="btn")}

</%forms:form>

<ul class="nav nav-pills">
    <li><a href="${request.route_url('delete_account')}">Delete your account</a></li>
</ul>


