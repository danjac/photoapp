    
PhotoApp = PhotoApp or {}

class PhotoApp.Message

    constructor: (@message) ->
    
    show: () ->

        html = "
        <div class=\"alert\">
            <button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>
            #{@message}
        </div>"
        $('#messages').append(html)


PhotoApp.showMessage = (message) ->
    new PhotoApp.Message(message).show()

 
class PhotoApp.Photo

    constructor: (el) ->
        @el = el

        @modal = $('#photo-modal')

        @imageURL = @el.attr 'data-image-url'
        @thumbURL = @el.attr 'data-thumbnail-url'
        @sendURL = @el.attr 'data-send-url'
        @deleteURL = @el.attr 'data-delete-url'

        @title = @el.attr 'data-title'
        @height = @el.attr 'data-height'
        @width = @el.attr 'data-width'

        @tmpl = $('#photo-modal-template').html()

        @content = _.template(@tmpl,
            image_url: @imageURL
            thumbnail_url: @thumbURL
            send_url: @sendURL
            delete_url: @deleteURL
            title: @title
            height: @height
            width: @width
        )


        @modal.on 'show', =>
            @modal.html(@content)

            if @deleteURL?
                $('#photo-modal .delete-btn').show().on 'click', => @delete()
            else
                $('#photo-modal .delete-btn').hide()


            progressBar = $('#photo-modal .photo-load-progress .bar')
            progressWidth = 0

            progress = setInterval =>
                if progressWidth < 100
                    progressWidth += 30
                    progressBar.width progressWidth + "%"


            image = new Image()
            image.src = @imageURL
        
            image.onload = =>

                clearInterval progress
                $('#photo-modal .photo-image').show()
                $('#photo-modal .photo-load-progress').hide()
        
        @modal.modal('show')

    delete: ->
        if confirm "Are you sure you want to delete this photo?"
            @modal.modal('hide')
            $.post @deleteURL, null, (response) =>
                if response.success?
                    @el.parent().remove()
                    PhotoApp.showMessage("Photo '#{@title}' has been deleted")
        false

class PhotoApp.PhotosPage

    constructor: (tagList) ->
        @tagList = tagList
        jQuery => @onload()

    onload: ->

        @doc = $(document)

        @tagCloud = $('#tag-cloud')
        @tagCloud.jQCloud(@tagList)
        @tagCloud.hide()

        @tagBtn = $('#tags-btn')

        @doc.on 'click', '.thumbnails a', (event) ->
            new PhotoApp.Photo($(@))
        
        @doc.on 'click', '#tags-btn', (event) =>

            @tagCloud.slideToggle('slow')

        $.ias
            container : '.thumbnails'
            item: '.photo'
            pagination: '.pagination'
            next: '.next a'



