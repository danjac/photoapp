var PhotoApp;

PhotoApp = PhotoApp || {};

PhotoApp.Photo = (function() {

  function Photo(el) {
    var _this = this;
    this.el = el;
    this.modal = $('#photo-modal');
    this.imageURL = this.el.attr('data-image-url');
    this.sendURL = this.el.attr('data-send-url');
    this.title = this.el.attr('data-title');
    this.height = this.el.attr('data-height');
    this.width = this.el.attr('data-width');
    this.tmpl = $('#photo-modal-template').html();
    this.content = _.template(this.tmpl, {
      image_url: this.imageURL,
      send_url: this.sendURL,
      title: this.title,
      height: this.height,
      width: this.width
    });
    this.modal.on('show', function() {
      var image, progress, progressBar, progressWidth;
      _this.modal.html(_this.content);
      progressBar = $('#photo-modal .photo-load-progress .bar');
      progressWidth = 0;
      progress = setInterval(function() {
        if (progressWidth < 100) {
          progressWidth += 20;
          return progressBar.width(progressWidth + "%");
        }
      });
      image = new Image();
      image.src = _this.imageURL;
      return image.onload = function() {
        clearInterval(progress);
        $('#photo-modal .photo-image').show();
        return $('#photo-modal .photo-load-progress').hide();
      };
    });
    this.modal.modal('show');
  }

  return Photo;

})();

PhotoApp.HomePage = (function() {

  function HomePage() {
    var _this = this;
    jQuery(function() {
      return _this.onload();
    });
  }

  HomePage.prototype.onload = function() {
    return $('.thumbnails a').on('click', function() {
      return new PhotoApp.Photo($(this));
    });
  };

  return HomePage;

})();
