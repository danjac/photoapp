
{% import "_forms.jinja2" as forms with context %}
{% call forms.render_form(form, id="edit-photo-form") %}

    <legend>Edit this photo</legend>

    {{ forms.render_field(form.title) }}
    {{ forms.render_field(form.taglist) }}
    {{ forms.render_checkbox_field(form.is_public) }}

    {{ form.submit(class="btn") }}

    <button class="btn cancel-btn" type="button">Cancel</button>

{% endcall %}

