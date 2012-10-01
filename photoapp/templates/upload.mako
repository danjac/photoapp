<%inherit file="layout.mako" />
<%namespace file="forms.mako" name="forms" />

<%text>
<script type="text/template" id="image-field-template">
<dd>
    <div class="control-group">
        <div class="controls">
            <input type="file" name="images-<%= numItems %>" />
            <a href="#" class="remove-upload-field"><i class="icon-remove"></i></a>
        </div>
    </div>
</dd>
</script>
</%text>

<%forms:render_form form="${form}" multipart="${True}">

    <legend>Upload up to three photos to your collection.</legend>

    ${forms.render_field(form.title)}
    ${forms.render_field(form.taglist)}
    ${forms.render_checkbox_field(form.is_public)}

    <label>Photos</label>
    <dl>
        % for image in form.images.entries:
        <dd>${forms.render_field(image, with_label=False)}
        % if loop.index > 1:
        <a href="#" class="remove-upload-field"><i class="icon-remove"></i></a>
        % endif
        </dd>
        % endfor

        % if form.images.entries|length < 6:
        <dd>
            <button type="button" class="upload-add-another-btn btn"><i class="icon-plus"></i> Add another</button>
        </dd>
        % endif

    </dl>
    ${form.submit(class="btn")}}
<%/forms:render_form>

