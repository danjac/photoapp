<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}" attrs="${dict(id='edit-photo-form')}">

    <legend>Edit this photo</legend>

    ${forms.render_field(form.title)}
    ${forms.render_field(form.taglist)}
    ${forms.render_checkbox_field(form.is_public)}

    ${form.submit(class="btn")}

    <button class="btn cancel-btn" type="button">Cancel</button>


</%forms:render_form>
