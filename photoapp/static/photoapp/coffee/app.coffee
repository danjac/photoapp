    
PhotoApp = {} unless PhotoApp?

class PhotoApp.Message

    constructor: (@message) ->
    
    show: () ->

        html = "
        <div class=\"alert alert-success\">
            <button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>
            #{@message}
        </div>"
        $('#messages').html(html).show()


PhotoApp.showMessage = (message) ->
    new PhotoApp.Message(message).show()

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

        @imageURL = @el.attr 'data-image-url'
        @thumbnailURL = @el.attr 'data-thumbnail-url'
        @downloadURL = @el.attr 'data-download-url'
        @sendURL = @el.attr 'data-send-url'
        @deleteURL = @el.attr 'data-delete-url'
        @deleteSharedURL = @el.attr 'data-delete-shared-url'
        @editURL = @el.attr 'data-edit-url'
        @shareURL = @el.attr 'data-share-url'
        @copyURL = @el.attr 'data-copy-url'

        @owner = @el.attr 'data-owner'
        @title = @el.attr 'data-title'
        @height = @el.attr 'data-height'
        @width = @el.attr 'data-width'

        @tmpl = $('#photo-modal-template').html()

        @content = _.template @tmpl, @


        @doc.on 'click', '#photo-modal .share-add-another-btn', (event) =>
            event.preventDefault()
            numItems = $("#share-photo-form input[type='text']").length

            newItem = "<dd><input type=\"text\" name=\"emails-#{ numItems - 1}\">
                <a href=\"#\" class=\"remove-share-email\"><i class=\"icon-remove\"></i></a>
                </dd>"
            $(event.currentTarget).parent().before(newItem)

        @doc.on 'click', '#photo-modal .remove-share-email', (event) =>
            event.preventDefault()
            $(event.currentTarget).parent().remove()

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
                    PhotoApp.showMessage(response.message)
            )
      
        @doc.on 'submit', '#send-photo-form', (event) =>
            event.preventDefault()
            @submitForm($('#send-photo-form'))

        @doc.on 'submit', '#edit-photo-form', (event) =>
            event.preventDefault()
            @submitForm($('#edit-photo-form'), (response) =>
                el = $("[data-photo-id='#{@photoID}']")
                el.attr('data-title', response.title)
                el.find('img').attr('title', response.title)
                $("#photo-modal h3").text(response.title)
            )

        @modal.on 'show', =>
            @modal.html(@content)

            if @editURL?
                $('#photo-modal .edit-btn').show().on 'click', => @edit()
            else
                $('#photo-modal .edit-btn').hide()

            if @shareURL?
                $('#photo-modal .share-btn').show().on 'click', => @share()
            else
                $('#photo-modal .share-btn').hide()

            if @sendURL?
                $('#photo-modal .send-btn').show().on 'click', => @send()
            else
                $('#photo-modal .send-btn').hide()

            if @copyURL?
                $('#photo-modal .copy-btn').show().on 'click', => @copy()
            else
                $('#photo-modal .copy-btn').hide()

            if @deleteURL?
                $('#photo-modal .delete-btn').show().on 'click', => @delete()
            else
                $('#photo-modal .delete-btn').hide()

            if @deleteSharedURL?
                $('#photo-modal .delete-shared-btn').show().on 'click', => @deleteShared()
            else
                $('#photo-modal .delete-shared-btn').hide()


            $('#photo-modal .send-btn').on 'click', => @send()

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

    submitForm: (form, callback) ->

        $.post(form.attr('action'), form.serialize(), (response) =>
            if response.success
                if response.message?
                    PhotoApp.showMessage response.message
                @showDefaultContent()
                if callback?
                    callback(response)
            else
                $('#photo-modal-load').html(response.html)
        )


    showDefaultContent: ->
        $('#photo-modal-load').hide()
        $('#photo-modal-content').show()
        $('#photo-modal-footer .buttons').show()

    showForm: (url) ->
        $('#photo-modal-content').hide()
        $('#photo-modal-footer .buttons').hide()

        $.get url, null, (response) =>
            $('#photo-modal-load').show().html(response.html)
            #$('#photo-modal-footer a').addClass('disabled')

    delete: ->
        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post @deleteURL, null, (response) =>
                if response.success?
                    @el.parent().remove()
                    PhotoApp.showMessage("Photo '#{@title}' has been deleted")

    send: -> @showForm @sendURL
       
    edit: -> @showForm @editURL

    share: -> @showForm @shareURL

    copy: -> @showForm @copyURL

    deleteShared: ->
        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post @deleteSharedURL, null, (response) =>
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
        maxUploads = 6

        $('.upload-add-another-btn').click (event) =>
            event.preventDefault()
            btn = $(event.currentTarget)
            numItems = $("form input[type='file']").length
            if numItems < maxUploads
                newItem = "<dd><input type=\"file\" name=\"images-#{ numItems - 1}\">
                    <a href=\"#\" class=\"remove-upload-field\"><i class=\"icon-remove\"></i></a>
                    </dd>"
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
                html = '<div class="well" id="tag-cloud" style="height:250px;"></div>'
                @searchBox.append(html)

                $('#tag-cloud').jQCloud(response.tags)
            else
                
        )

    onload: ->

        @doc = $(document)

        @searchBox = $('#search-box')
        @searchBox.hide()

        @searchBtn = $('#search-btn')

        @doc.on 'click', '.thumbnails a', (event) =>
            new PhotoApp.Photo(@, $(event.currentTarget))
        
        @doc.on 'click', '#search-btn', (event) =>

            @searchBox.slideToggle 'slow'
            @searchBtn.toggleClass 'btn-primary'

            icon = @searchBtn.find 'i'
            icon.toggleClass 'icon-white'

            unless @searchBtn.is '.btn-primary'
                @loadTags()

            false


        PhotoApp.paginate()

