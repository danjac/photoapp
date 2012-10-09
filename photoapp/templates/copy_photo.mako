
<%namespace file="forms.mako" name="forms" />

<%forms:form form="${form}"
             legend="Add this photo to your own collection"
             id="copy-photo-form">


    ${forms.field(form.title)}
    ${forms.field(form.taglist)}
    ${form.submit(value='Add', class_='btn')}
    ${forms.cancel()}


</%forms:form>
