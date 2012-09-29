<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}" attrs="${dict(id='copy-photo-form')}">

    <legend>Share this photo</legend>

    <p>Enter the email addresses of the people you want to share this
    photo with. If they haven't joined this site yet, we'll send them
    an invite.</p>

    <label>Recipients</label>

    <dl class="share-email-list">

        % for counter, item in enumerate(form.emails.entries):
        <dd>
            <div class="control-group">
                <div class="controls">
                    <input type="text" name="emails-${counter}">
                    % if loop.index > 0:
                    <a href="#" class="remove-share-email"><i class="icon-remove"></i></a>
                    % endif
                    ${forms.render_errors(item)}
                </div>
            </div>
        </dd>
        % endfor

        <dd>
            <button type="button" class="share-add-another-btn btn"><i class="icon-plus"></i> Add another</button>
        </dd>

    </dl>

    ${forms.render_field(form.note)}
    ${form.submit(class_="btn")}

    <button class="btn cancel-btn" type="button">Cancel</button>

</%forms:render_form>
