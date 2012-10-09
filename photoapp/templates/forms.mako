
<%def name="form(form, action=None, legend=None, **attrs)">
<% action = action or request.current_route_url() %>
${h.form(action, **attrs)}

% if legend:
<legend>${legend}</legend>
% endif

${csrf_token()}

%for field in form:
    % if field.type == 'HiddenField':
    ${field}
    % endif
%endfor
${caller.body()}
${h.end_form()}

</%def>

<%def name="errors(errorlist)">
    % for error in errorlist:
    <span class="help-inline">${error}</span>
    % endfor
</%def>

<%def name="field(field, **attrs)">
    <div class="control-group ${'error' if field.errors else ''}">
        <div class="controls">
        % if field.type == 'BooleanField':
        <label class="checkbox">${field.label.text}
        % else:
        ${field.label(class_="control-label")}
        % endif
        ${field(**attrs)}
        ${errors(field.errors)}
        % if field.type == 'BooleanField':
        </label>
        % endif
        </div>
    </div>
</%def>

<%def name="csrf_token()">
${h.hidden('csrf_token', value=request.session.get_csrf_token())}
</%def>
