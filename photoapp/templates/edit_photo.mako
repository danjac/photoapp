
<%namespace file="forms.mako" name="forms" />
<%forms:form form="${form}"
             legend="Edit this photo"
             id="edit-photo-form">


    ${forms.field(form.title)}
    ${forms.field(form.taglist)}
    ${forms.field(form.is_public)}

    ${form.submit(class_="btn")}
    ${forms.cancel()}


</%forms:form>
