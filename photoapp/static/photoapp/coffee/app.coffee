    
PhotoApp = PhotoApp or {}

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
        confirm 'Are you sure you want to delete this photo?'


class PhotoApp.PhotosPage

    constructor: (tagList) ->
        @tagList = tagList
        jQuery => @onload()

    onload: ->

        $('#tag-cloud').jQCloud(@tagList)

        $('.thumbnails a').on 'click', ->
            new PhotoApp.Photo($(@))
        
        $.ias
            container : '.thumbnails'
            item: '.photo'
            pagination: '.pagination'
            next: '.next a'



