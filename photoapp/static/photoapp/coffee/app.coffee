

PhotoApp = {} unless PhotoApp?

class PhotoApp.Message

    constructor: (@message, @target="#messages") ->
        @tmpl = $('#message-template').html()

    show: () ->
        $(@target).html(_.template(@tmpl, @)).show().fadeOut(3000)


PhotoApp.showMessage = (message, target) ->
    new PhotoApp.Message(message, target).show()

PhotoApp.paginate = ->
    # sets up infinite scrolling
    $.ias
        container : '.thumbnails'
        item: '.photo'
        pagination: '.pagination'
        next: '.next a'
        loader: '<img src="ias/loader.gif">'


class PhotoApp.Photo

    constructor: (@page, @el) ->
        @doc = @page.doc

        @modal = $('#photo-modal')

        @photoID = @el.attr 'data-photo-id'
        @isPublic = @el.attr 'data-is-public'

        @imageURL = @el.attr 'data-image-url'
        @thumbnailURL = @el.attr 'data-thumbnail-url'
        @downloadURL = @el.attr 'data-download-url'
        @deleteURL = @el.attr 'data-delete-url'
        @deleteSharedURL = @el.attr 'data-delete-shared-url'
        @editURL = @el.attr 'data-edit-url'
        @shareURL = @el.attr 'data-share-url'
        @copyURL = @el.attr 'data-copy-url'

        @owner = @el.attr 'data-owner'
        @ownerURL = @el.attr 'data-owner-url'
        @title = @el.attr 'data-title'
        @height = @el.attr 'data-height'
        @width = @el.attr 'data-width'

        @modalTmpl = $('#photo-modal-template').html()
        @shareFieldTmpl = $('#share-field-template').html()

        @contacts = []
        @render()

        # clear old events
        #
        @doc.off 'submit', '#edit-photo-form'
        @doc.off 'submit', '#copy-photo-form'
        @doc.off 'submit', '#share-photo-form'

        @doc.off 'click', '#photo-modal .share-add-another-btn'
        @doc.off 'click', '#photo-modal .remove-share-email'
        @doc.off 'click', '#photo-modal .cancel-btn'
        @doc.off 'click', '#photo-modal .edit-btn'
        @doc.off 'click', '#photo-modal .share-btn'
        @doc.off 'click', '#photo-modal .copy-btn'
        @doc.off 'click', '#photo-modal .delete-btn'
        @doc.off 'click', '#photo-modal .delete-shared-btn'
        @doc.off 'click', '#photo-modal .permalink-btn'
        @doc.off 'click', '#photo-modal .close-permalink-btn'

        @doc.on 'click', '#photo-modal .permalink-btn', (event) =>
            event.preventDefault()
            @hideButtons()

            if @isPublic
                $('#photo-modal .permalink-container-is-public').show()
            else
                $('#photo-modal .permalink-container-is-private').show()

            $('#photo-modal input.permalink').focus().select()

        @doc.on 'click', '#photo-modal .close-permalink-btn', (event) =>
            event.preventDefault()
            $('#photo-modal .permalink-container').hide()
            @showButtons()

        @doc.on 'click', '#photo-modal .share-add-another-btn', (event) =>
            event.preventDefault()
            numItems = $("#share-photo-form input[type='text']").length
            newItem = _.template(@shareFieldTmpl, {numItems: numItems})
            $(event.currentTarget).parent().before(newItem)
            @shareAutoComplete()

        @doc.on 'click', '#photo-modal .remove-share-email', (event) =>
            event.preventDefault()
            $(event.currentTarget).closest('dd').remove()

        @doc.on 'click', '#photo-modal .cancel-btn', (event) =>
            event.preventDefault()
            @showDefaultContent()

        @doc.on 'submit', '#share-photo-form', (event) =>
            event.preventDefault()
            @submitForm($('#share-photo-form'))

        @doc.on 'submit', '#copy-photo-form', (event) =>
            event.preventDefault()
            @modal.modal('hide')
            @submitForm($('#copy-photo-form'), (response) =>
                if response.success?
                    @el.parent().remove()
                    @showMessage(response.message)
            )

        @doc.on 'submit', '#edit-photo-form', (event) =>
            event.preventDefault()
            @submitForm($('#edit-photo-form'), (response) =>
                @title = response.title
                @el.attr 'data-title', @title

                if response.is_public
                    @el.attr 'data-is-public', '1'
                    @isPublic = true
                else
                    @el.removeAttr 'data-is-public'
                    @isPublic = false

                img = @el.find 'img'
                img.attr 'alt', @title
                img.attr 'title', @title
                @modal.find('h3').text @title
                @modal.modal('show')

            )

        @renderButton '#photo-modal .edit-btn', @editURL, @edit
        @renderButton '#photo-modal .share-btn', @shareURL, @share
        @renderButton '#photo-modal .copy-btn', @copyURL, @copy
        @renderButton '#photo-modal .delete-btn', @deleteURL, @delete
        @renderButton '#photo-modal .delete-shared-btn', @deleteSharedURL, @deleteShared

        @modal.on 'show', =>

            progressBar = $('#photo-modal .photo-load-progress .bar')
            progressWidth = 0

            setProgressWidth = ->
                if progressWidth < 100
                    progressWidth += 5
                    progressBar.width progressWidth + "%"

            progress = setInterval setProgressWidth, 300

            image = new Image()
            image.src = @thumbnailURL

            image.onload = =>

                clearInterval progress
                $('#photo-modal .photo-image').show()
                $('#photo-modal .photo-load-progress').hide()
                $('#photo-modal-footer').show()

        @modal.modal('show')

    render: ->
        @modal.html(_.template @modalTmpl, @)

    renderButton: (btn, url, onClick) ->

        if url?
            $(btn).show().on 'click', (event) =>
                event.preventDefault()
                onClick(event)

        else
            $(btn).hide()

    showMessage: (message) ->
        PhotoApp.showMessage message, "#photo-modal .messages"

    submitForm: (form, callback) ->

        $.post(form.attr('action'), form.serialize(), (response) =>
            if response.success
                if response.message?
                    @showMessage response.message
                @showDefaultContent()
                if callback?
                    callback(response)
            else
                $('#photo-modal-load').html(response.html)
        )

    showButtons: ->
        $('#photo-modal-footer .buttons').show()

    hideButtons: ->
        $('#photo-modal-footer .buttons').hide()

    showDefaultContent: ->
        $('#photo-modal-load').hide()
        $('#photo-modal-content').show()
        @showButtons()

    showForm: (url, callback) ->
        $('#photo-modal-content').hide()
        @hideButtons()

        $.get url, null, (response) =>
            $('#photo-modal-load').show().html(response.html)

            if callback?
                callback(response)

    delete: ->
        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post @deleteURL, null, (response) =>
                if response.success?
                    @el.parent().remove()
                    PhotoApp.showMessage("Photo '#{@title}' has been deleted")

    edit: => @showForm @editURL

    shareAutoComplete: =>
        $('.share-email-field').autocomplete
            source: @contacts
            dataType: "json"

    share: => @showForm @shareURL, (response) =>
        @contacts = response.contacts
        @shareAutoComplete()

    copy: => @showForm @copyURL

    delete: => @deleteAction @deleteURL

    deleteShared: => @deleteAction @deleteSharedURL

    deleteAction: (deleteURL) ->

        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post deleteURL, null, (response) =>
                if response.success?
                    @el.parent().remove()
                    PhotoApp.showMessage("Photo '#{@title}' has been deleted")



class PhotoApp.SharedPage

    constructor: ->
        jQuery => @onload()

    onload: ->
        PhotoApp.paginate()


class PhotoApp.UploadPage

    constructor: ->

        jQuery => @onload()

    onload: ->
        @doc = $(document)
        @imageFieldTmpl = $('#image-field-template').html()
        maxUploads = 3

        $('.upload-add-another-btn').click (event) =>
            event.preventDefault()
            btn = $(event.currentTarget)
            numItems = $("form input[type='file']").length

            if numItems < maxUploads
                newItem = _.template(@imageFieldTmpl, {numItems: numItems})
                btn.parent().before(newItem)
                if (numItems + 1) >= maxUploads
                    btn.parent().hide()

        @doc.on 'click', '.remove-upload-field', (event) =>
            event.preventDefault()
            $(event.currentTarget).parent().remove()
            numItems = $("form input[type='file']").length
            if numItems < maxUploads
                $('.upload-add-another-btn').parent().show()


class PhotoApp.PhotosPage

    constructor: (@tagsURL) ->
        jQuery => @onload()

    loadTags: ->

        $('#tag-cloud').remove()

        $.get(@tagsURL, null, (response) =>

            if response.tags.length > 0
                @searchBox.append(@tagCloudHtml)

                $('#tag-cloud').jQCloud(response.tags)

        )

    onload: ->

        @doc = $(document)

        @searchBox = $('#search-box')
        @searchBox.hide()

        @searchBtn = $('#search-btn')

        @tagCloudHtml = $('#tag-cloud-template').html()

        @doc.on 'click', 'a.thumbnail', (event) =>
            event.preventDefault()
            new PhotoApp.Photo(@, $(event.currentTarget))

        @doc.on 'click', '#search-btn', (event) =>
            event.preventDefault()

            @searchBox.slideToggle 'slow'
            @searchBtn.toggleClass 'btn-primary'

            icon = @searchBtn.find 'i'
            icon.toggleClass 'icon-white'

            unless @searchBtn.is '.btn-primary'
                @loadTags()

        PhotoApp.paginate()
