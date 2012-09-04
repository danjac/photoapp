var PhotoApp;

PhotoApp = PhotoApp || {};

PhotoApp.Message = (function() {

  function Message(message) {
    this.message = message;
  }

  Message.prototype.show = function() {
    var html;
    html = "        <div class=\"alert alert-success\">            <button type=\"button\" class=\"close\" data-dismiss=\"alert\">&times;</button>            " + this.message + "        </div>";
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
    this.doc = $(document);
    this.modal = $('#photo-modal');
    this.photoID = this.el.attr('data-photo-id');
    this.imageURL = this.el.attr('data-image-url');
    this.thumbURL = this.el.attr('data-thumbnail-url');
    this.sendURL = this.el.attr('data-send-url');
    this.deleteURL = this.el.attr('data-delete-url');
    this.editURL = this.el.attr('data-edit-url');
    this.title = this.el.attr('data-title');
    this.height = this.el.attr('data-height');
    this.width = this.el.attr('data-width');
    this.tmpl = $('#photo-modal-template').html();
    this.content = _.template(this.tmpl, {
      image_url: this.imageURL,
      thumbnail_url: this.thumbURL,
      title: this.title,
      height: this.height,
      width: this.width
    });
    this.doc.on('click', '#photo-modal .cancel-btn', function(event) {
      return _this.showDefaultContent();
    });
    this.doc.on('submit', '#send-photo-form', function(event) {
      _this.submitForm($('#send-photo-form'));
      return false;
    });
    this.doc.on('submit', '#edit-photo-form', function(event) {
      _this.submitForm($('#edit-photo-form'), function(response) {
        alert(response.title);
        $("[data-photo-id]='" + _this.photoID + "'").attr('data-title', response.title);
        $("[data-photo-id]='" + _this.photoID + "' img").attr(title, response.title);
        return $("#photo-modal h3").text(response.title);
      });
      return false;
    });
    this.modal.on('show', function() {
      var image, progress, progressBar, progressWidth, setProgressWidth;
      _this.modal.html(_this.content);
      if (_this.editURL != null) {
        $('#photo-modal .edit-btn').show().on('click', function() {
          return _this.edit();
        });
      } else {
        $('#photo-modal .edit-btn').hide();
      }
      if (_this.deleteURL != null) {
        $('#photo-modal .delete-btn').show().on('click', function() {
          return _this["delete"]();
        });
      } else {
        $('#photo-modal .delete-btn').hide();
      }
      $('#photo-modal .send-btn').on('click', function() {
        return _this.send();
      });
      progressBar = $('#photo-modal .photo-load-progress .bar');
      progressWidth = 0;
      setProgressWidth = function() {
        if (progressWidth < 100) {
          progressWidth += 5;
          return progressBar.width(progressWidth + "%");
        }
      };
      progress = setInterval(setProgressWidth, 300);
      image = new Image();
      image.src = _this.imageURL;
      return image.onload = function() {
        clearInterval(progress);
        $('#photo-modal .photo-image').show();
        $('#photo-modal .photo-load-progress').hide();
        return $('#photo-modal-footer').show();
      };
    });
    this.modal.modal('show');
  }

  Photo.prototype.submitForm = function(form, callback) {
    var _this = this;
    $.post(form.attr('action'), form.serialize(), function(response) {
      if (response.success) {
        if (response.message != null) {
          PhotoApp.showMessage(response.message);
        }
        _this.showDefaultContent();
        if (callback != null) {
          return callback(response);
        }
      } else {
        return $('#photo-modal-load').html(response.html);
      }
    });
    return false;
  };

  Photo.prototype.showDefaultContent = function() {
    $('#photo-modal-load').hide();
    return $('#photo-modal-content').show();
  };

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

  Photo.prototype.send = function() {
    var _this = this;
    $('#photo-modal-content').hide();
    $.get(this.sendURL, null, function(response) {
      return $('#photo-modal-load').show().html(response.html);
    });
    return false;
  };

  Photo.prototype.edit = function() {
    var _this = this;
    $('#photo-modal-content').hide();
    $.get(this.editURL, null, function(response) {
      return $('#photo-modal-load').show().html(response.html);
    });
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
    var _this = this;
    this.doc = $(document);
    if (this.tagList != null) {
      this.tagCloud = $('#tag-cloud');
      this.tagCloud.jQCloud(this.tagList);
      this.tagCloud.hide();
    }
    this.tagBtn = $('#tags-btn');
    if (!(this.tagList != null)) {
      this.tagBtn.remove();
    }
    this.doc.on('click', '.thumbnails a', function(event) {
      return new PhotoApp.Photo($(this));
    });
    this.doc.on('click', '#tags-btn', function(event) {
      var icon;
      _this.tagCloud.slideToggle('slow');
      _this.tagBtn.toggleClass('btn-primary');
      icon = _this.tagBtn.find('i');
      icon.toggleClass('icon-white');
      return false;
    });
    return $.ias({
      container: '.thumbnails',
      item: '.photo',
      pagination: '.pagination',
      next: '.next a',
      loader: '<img src="ias/loader.gif">'
    });
  };

  return PhotosPage;

})();
