
<%namespace file="forms.mako" name="forms" />

<$forms:form form="${form}" id="delete-photo-form">

    <p class=well>
        Are you sure you want to remove this photo?
    </p>

    <button class="btn btn-primary cancel-btn" type="button">Cancel</button>
    <button type="submit" class="btn btn-danger logout">Go ahead</button>

</%forms:form>
