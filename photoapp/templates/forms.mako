
<%def name="render_form(form, method='POST', action=None, multipart=False, attrs=None)">
<% attrs = attrs or {} %>
<form method="${method}" action="${action or request.url}" ${'enctype="multipart/form-data"' if multipart else ''} ${' '.join('%s="%s"' % (k, v) for k, v in attrs.iteritems())|n}>
   ${form.csrf_token}
   ${caller.body()}
</form>
</%def>

<%def name="render_errors(field)">
% for error in field.errors:
<span class="help-inline">${error}</span>
% endfor
</%def>

<%def name="render_field(field, attrs=None)">
<% attrs = attrs or {} %>
<div class="control-group ${'error' if field.errors else ''}">
    <div class="controls">
    % if attrs.pop('with_label', True):
    ${field.label(class_="control-label")}
    % endif
    ${field(**attrs)}
    ${render_errors(field)}
    </div>
</div>
</%def>

<%def name="render_checkbox_field(field)">
<div class="control-group ${'error' if field.errors else ''}">
    <div class="controls">
        <label class="checkbox">${field.label.text}
        ${field(**kwargs)}
        ${render_errors(field)}
        </label>
    </div>
</div>
</%def>






