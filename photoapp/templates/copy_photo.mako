<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}" attrs="${dict(id='copy-photo-form')}">
    <legend>Add this photo to your own collection</legend>

    ${forms.render_field(form.title)}
    ${forms.render_field(form.taglist)}

    ${form.submit(value="Add", class="btn")}

    <button class="btn cancel-btn" type="button">Cancel</button>

</%forms>
