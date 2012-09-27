<%inherit file="layout.mako" />
<%namespace file="forms.mako" name="forms" />

<%forms:render_form form="${form}" attrs="${dict(onsubmit='navigator.id.logout(); return true;')}">
    <p>
        Are you sure you want to delete your account? You will lose <b>ALL</b> your photos!
    </p>
    <a href="{{ request.route_url('settings') }}" class="btn btn-primary">Cancel</a>
    <button type="submit" class="btn btn-danger logout">Go ahead</button>
</%forms:render_form>
