
<%inherit file="base.mako" />
<%namespace file="forms.mako" name="forms" />

<%forms:form form="${form}"
             action="${request.route_url('signup')}"
             legend="Sign up to get started">

    ${forms.field(form.first_name)}
    ${forms.field(form.last_name)}
    ${forms.field(form.email)}

    ${form.submit(class_="btn")}

</%forms:form>


