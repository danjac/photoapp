var PhotoApp;

PhotoApp = PhotoApp || {};

PhotoApp.Message = (function() {

  function Message(message) {
    this.message = message;
  }

  Message.prototype.show = function() {
    var html;
    html = "        <div class=\"alert\">            <button type=\"button\" class=\"close\" data-dismiss=\"alert\">×</button>            " + this.message + "        </div>";
    return $('#messages').append(html);
  };

  return Message;

})();

PhotoApp.showMessage = function(message) {
  return new PhotoApp.Message(message).show();
};

PhotoApp.Photo = (function() {

  function Photo(el) {
    var _this = this;
    this.el = el;
    this.modal = $('#photo-modal');
    this.imageURL = this.el.attr('data-image-url');
    this.thumbURL = this.el.attr('data-thumbnail-url');
    this.sendURL = this.el.attr('data-send-url');
    this.deleteURL = this.el.attr('data-delete-url');
    this.title = this.el.attr('data-title');
    this.height = this.el.attr('data-height');
    this.width = this.el.attr('data-width');
    this.tmpl = $('#photo-modal-template').html();
    this.content = _.template(this.tmpl, {
      image_url: this.imageURL,
      thumbnail_url: this.thumbURL,
      send_url: this.sendURL,
      delete_url: this.deleteURL,
      title: this.title,
      height: this.height,
      width: this.width
    });
    this.modal.on('show', function() {
      var image, progress, progressBar, progressWidth;
      _this.modal.html(_this.content);
      if (_this.deleteURL != null) {
        $('#photo-modal .delete-btn').show().on('click', function() {
          return _this["delete"]();
        });
      } else {
        $('#photo-modal .delete-btn').hide();
      }
      progressBar = $('#photo-modal .photo-load-progress .bar');
      progressWidth = 0;
      progress = setInterval(function() {
        if (progressWidth < 100) {
          progressWidth += 30;
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

  Photo.prototype["delete"] = function() {
    var _this = this;
    if (confirm("Are you sure you want to delete this photo?")) {
      this.modal.modal('hide');
      $.post(this.deleteURL, null, function(response) {
        if (response.success != null) {
          _this.el.parent().remove();
          return PhotoApp.showMessage("Photo '" + _this.title + "' has been deleted");
        }
      });
    }
    return false;
  };

  return Photo;

})();

PhotoApp.PhotosPage = (function() {

  function PhotosPage(tagList) {
    var _this = this;
    this.tagList = tagList;
    jQuery(function() {
      return _this.onload();
    });
  }

  PhotosPage.prototype.onload = function() {
    this.doc = $(document);
    $('#tag-cloud').jQCloud(this.tagList);
    this.doc.on('click', '.thumbnails a', function(event) {
      return new PhotoApp.Photo($(this));
    });
    return $.ias({
      container: '.thumbnails',
      item: '.photo',
      pagination: '.pagination',
      next: '.next a'
    });
  };

  return PhotosPage;

})();
