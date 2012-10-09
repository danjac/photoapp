
<%inherit file="base.mako" />
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

<%forms:form form="${form}"
             multipart="${True}"
             legend="Upload up to three photos to your collection.">

    ${forms.field(form.title)}
    ${forms.field(form.taglist)}
    ${forms.field(form.is_public)}

    <label>Photos</label>
    <dl>
        % for counter, image in enumerate(form.images.entries):
        <dd>${forms.field(image, with_label=False)}

            % if counter > 0:
            <a href="#" class="remove-upload-field"><i class="icon-remove"></i></a>
            % endif

        </dd>

        % endfor
        % if len(form.images.entries) < 6:
        <dd>
            <button type="button" class="upload-add-another-btn btn"><i class="icon-plus"></i> Add another</button>
        </dd>
        % endif

    </dl>

    ${form.submit(class_="btn")}

</%forms:form>


<%block name="scripts">
<script>
    var page = new PhotoApp.UploadPage;
</script>

</%block>
