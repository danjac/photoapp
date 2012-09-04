    
PhotoApp = PhotoApp or {}

class PhotoApp.Message

    constructor: (@message) ->
    
    show: () ->

        html = "
        <div class=\"alert alert-success\">
            <button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>
            #{@message}
        </div>"
        $('#messages').html(html)


PhotoApp.showMessage = (message) ->
    new PhotoApp.Message(message).show()

 
class PhotoApp.Photo

    constructor: (@page, @el) ->
        @doc = @page.doc

        @modal = $('#photo-modal')

        @photoID = @el.attr 'data-photo-id'

        @imageURL = @el.attr 'data-image-url'
        @thumbURL = @el.attr 'data-thumbnail-url'

        @sendURL = @el.attr 'data-send-url'
        @deleteURL = @el.attr 'data-delete-url'
        @editURL = @el.attr 'data-edit-url'

        @title = @el.attr 'data-title'
        @height = @el.attr 'data-height'
        @width = @el.attr 'data-width'

        @tmpl = $('#photo-modal-template').html()

        @content = _.template(@tmpl,
            image_url: @imageURL
            thumbnail_url: @thumbURL
            title: @title
            height: @height
            width: @width
        )


        @doc.on 'click', '#photo-modal .cancel-btn', (event) =>
            @showDefaultContent()
        
        @doc.on 'submit', '#send-photo-form', (event) =>
            @submitForm($('#send-photo-form'))
            false

        @doc.on 'submit', '#edit-photo-form', (event) =>

            @submitForm($('#edit-photo-form'), (response) =>
                el = $("[data-photo-id='#{@photoID}']")
                el.attr('data-title', response.title)
                el.find('img').attr('title', response.title)
                $("#photo-modal h3").text(response.title)
                @page.loadTags()
            )

            false
           
        @modal.on 'show', =>
            @modal.html(@content)

            if @editURL?
                $('#photo-modal .edit-btn').show().on 'click', => @edit()
            else
                $('#photo-modal .edit-btn').hide()

 
            if @deleteURL?
                $('#photo-modal .delete-btn').show().on 'click', => @delete()
            else
                $('#photo-modal .delete-btn').hide()

            $('#photo-modal .send-btn').on 'click', => @send()

            progressBar = $('#photo-modal .photo-load-progress .bar')
            progressWidth = 0

            setProgressWidth = ->
                if progressWidth < 100
                    progressWidth += 5
                    progressBar.width progressWidth + "%"

            progress = setInterval setProgressWidth, 300

            image = new Image()
            image.src = @imageURL
        
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
        false


    showDefaultContent: ->
        $('#photo-modal-load').hide()
        $('#photo-modal-content').show()

    showForm: (url) ->
        $('#photo-modal-content').hide()
        $.get url, null, (response) =>
            $('#photo-modal-load').show().html(response.html)
            #$('#photo-modal-footer a').addClass('disabled')

        false
 
    delete: ->
        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post @deleteURL, null, (response) =>
                if response.success?
                    @el.parent().remove()
                    PhotoApp().showMessage("Photo '#{@title}' has been deleted")
                    @page.loadTags()
        false

    send: -> @showForm @sendURL
       
    edit: -> @showForm @editURL


class PhotoApp.PhotosPage

    constructor: (@tagsURL) ->
        jQuery => @onload()

    loadTags: ->

         @tagCloud.html('')

         $.get(@tagsURL, null, (response) =>
            @tagCloud.jQCloud(response.tags)
            @tagCloud.hide()
            if not response.tags
                @tagBtn.hide()
            else
                @tagBtn.addClass 'btn-primary'
                @tagBtn.find('i').addClass 'icon-white'
         )
       
    onload: ->

        @doc = $(document)

        @tagCloud = $('#tag-cloud')

        @tagBtn = $('#tags-btn')
        @loadTags()

        @doc.on 'click', '.thumbnails a', (event) =>
            new PhotoApp.Photo(@, $(event.currentTarget))
        
        @doc.on 'click', '#tags-btn', (event) =>

            @tagCloud.slideToggle 'slow'
            @tagBtn.toggleClass 'btn-primary'

            icon = @tagBtn.find 'i'
            icon.toggleClass 'icon-white'

            false

        $.ias
            container : '.thumbnails'
            item: '.photo'
            pagination: '.pagination'
            next: '.next a'
            loader: '<img src="ias/loader.gif">'



