<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}" attrs="${dict(id='copy-photo-form')}">

    <legend>Share this photo</legend>

    <p>Enter the email addresses of the people you want to share this
    photo with. If they haven't joined this site yet, we'll send them
    an invite.</p>

    <label>Recipients</label>

    % for counter, item in enumerate(form.emails.entries):
    <div class="control-group">
        <div class="controls">
            ${item}
            % if counter > 0:
            <a href="#" class="remove-share-email"><i class="icon-remove"></i></a>
            % endif
            ${forms.render_errors(item)}
        </div>
    </div>
    % endfor

    <button type="button" class="share-add-another-btn btn"><i class="icon-plus"></i> Add another</button>
    ${form.submit(class_="btn")}
    <button class="btn cancel-btn" type="button">Cancel</button>


</%forms:render_form>
