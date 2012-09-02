    
PhotoApp = PhotoApp or {}

class PhotoApp.Photo

    constructor: (el) ->
        @el = el

        @modal = $('#photo-modal')

        @imageURL = @el.attr 'data-image-url'
        @sendURL = @el.attr 'data-send-url'
        @title = @el.attr 'data-title'
        @height = @el.attr 'data-height'
        @width = @el.attr 'data-width'

        @tmpl = $('#photo-modal-template').html()

        @content = _.template(@tmpl,
            image_url: @imageURL
            send_url: @sendURL
            title: @title
            height: @height
            width: @width
        )

        @modal.on 'show', =>
            @modal.html(@content)

            progressBar = $('#photo-modal .photo-load-progress .bar')
            progressWidth = 0

            progress = setInterval =>
                if progressWidth < 100
                    progressWidth += 20
                    progressBar.width progressWidth + "%"


            image = new Image()
            image.src = @imageURL
        
            image.onload = =>

                clearInterval progress
                $('#photo-modal .photo-image').show()
                $('#photo-modal .photo-load-progress').hide()
        
        @modal.modal('show')


class PhotoApp.HomePage

    constructor: ->
        jQuery => @onload()

    onload: ->

        $('.thumbnails a').on 'click', ->
            new PhotoApp.Photo($(@))
               
        



