var PhotoApp;PhotoApp=PhotoApp||{},PhotoApp.Message=function(){function a(a){this.message=a}return a.prototype.show=function(){var a;return a='        <div class="alert alert-success">            <button type="button" class="close" data-dismiss="alert">&times;</button>            '+this.message+"        </div>",$("#messages").html(a)},a}(),PhotoApp.showMessage=function(a){return(new PhotoApp.Message(a)).show()},PhotoApp.Photo=function(){function a(a,b){var c=this;this.page=a,this.el=b,this.doc=this.page.doc,this.modal=$("#photo-modal"),this.photoID=this.el.attr("data-photo-id"),this.imageURL=this.el.attr("data-image-url"),this.thumbURL=this.el.attr("data-thumbnail-url"),this.sendURL=this.el.attr("data-send-url"),this.deleteURL=this.el.attr("data-delete-url"),this.editURL=this.el.attr("data-edit-url"),this.title=this.el.attr("data-title"),this.height=this.el.attr("data-height"),this.width=this.el.attr("data-width"),this.tmpl=$("#photo-modal-template").html(),this.content=_.template(this.tmpl,{image_url:this.imageURL,thumbnail_url:this.thumbURL,title:this.title,height:this.height,width:this.width}),this.doc.on("click","#photo-modal .cancel-btn",function(a){return c.showDefaultContent()}),this.doc.on("submit","#send-photo-form",function(a){return c.submitForm($("#send-photo-form")),!1}),this.doc.on("submit","#edit-photo-form",function(a){return c.submitForm($("#edit-photo-form"),function(a){return b=$("[data-photo-id='"+c.photoID+"']"),b.attr("data-title",a.title),b.find("img").attr("title",a.title),$("#photo-modal h3").text(a.title),c.page.loadTags()}),!1}),this.modal.on("show",function(){var a,b,d,e,f;return c.modal.html(c.content),c.editURL!=null?$("#photo-modal .edit-btn").show().on("click",function(){return c.edit()}):$("#photo-modal .edit-btn").hide(),c.deleteURL!=null?$("#photo-modal .delete-btn").show().on("click",function(){return c["delete"]()}):$("#photo-modal .delete-btn").hide(),$("#photo-modal .send-btn").on("click",function(){return c.send()}),d=$("#photo-modal .photo-load-progress .bar"),e=0,f=function(){if(e<100)return e+=5,d.width(e+"%")},b=setInterval(f,300),a=new Image,a.src=c.thumbURL,a.onload=function(){return clearInterval(b),$("#photo-modal .photo-image").show(),$("#photo-modal .photo-load-progress").hide(),$("#photo-modal-footer").show()}}),this.modal.modal("show")}return a.prototype.submitForm=function(a,b){var c=this;return $.post(a.attr("action"),a.serialize(),function(a){if(!a.success)return $("#photo-modal-load").html(a.html);a.message!=null&&PhotoApp.showMessage(a.message),c.showDefaultContent();if(b!=null)return b(a)}),!1},a.prototype.showDefaultContent=function(){return $("#photo-modal-load").hide(),$("#photo-modal-content").show()},a.prototype.showForm=function(a){var b=this;return $("#photo-modal-content").hide(),$.get(a,null,function(a){return $("#photo-modal-load").show().html(a.html)}),!1},a.prototype["delete"]=function(){var a=this;return confirm("Are you sure you want to delete this photo?")&&(this.modal.modal("hide"),$.post(this.deleteURL,null,function(b){if(b.success!=null)return a.el.parent().remove(),PhotoApp().showMessage("Photo '"+a.title+"' has been deleted"),a.page.loadTags()})),!1},a.prototype.send=function(){return this.showForm(this.sendURL)},a.prototype.edit=function(){return this.showForm(this.editURL)},a}(),PhotoApp.PhotosPage=function(){function a(a,b){var c=this;this.tagsURL=a,this.showSearch=b,jQuery(function(){return c.onload()})}return a.prototype.loadTags=function(){var a=this;return this.tagCloud.html(""),$.get(this.tagsURL,null,function(b){a.tagCloud.jQCloud(b.tags),b.tags||a.tagCloud.hide();if(a.showSearch!=null)return a.searchBtn.trigger("click")})},a.prototype.onload=function(){var a=this;return this.doc=$(document),this.tagCloud=$("#tag-cloud"),this.searchBox=$("#search-box"),this.searchBtn=$("#search-btn"),this.loadTags(),this.doc.on("click",".thumbnails a",function(b){return new PhotoApp.Photo(a,$(b.currentTarget))}),this.doc.on("click","#search-btn",function(b){var c;return a.searchBox.slideToggle("slow"),a.searchBtn.toggleClass("btn-primary"),c=a.searchBtn.find("i"),c.toggleClass("icon-white"),!1}),$.ias({container:".thumbnails",item:".photo",pagination:".pagination",next:".next a",loader:'<img src="ias/loader.gif">'})},a}();