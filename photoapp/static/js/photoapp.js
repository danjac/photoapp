var PhotoApp,__bind=function(a,b){return function(){return a.apply(b,arguments)}};if(typeof PhotoApp=="undefined"||PhotoApp===null)PhotoApp={};PhotoApp.Message=function(){function a(a,b){this.message=a,this.target=b!=null?b:"#messages",this.tmpl=$("#message-template").html()}return a.prototype.show=function(){return $(this.target).html(_.template(this.tmpl,this)).show().fadeOut(3e3)},a}(),PhotoApp.options==null&&(PhotoApp.options={}),PhotoApp.showMessage=function(a,b){return(new PhotoApp.Message(a,b)).show()},PhotoApp.configure=function(a){var b,c,d;console.log(a),d=[];for(b in a)c=a[b],d.push(PhotoApp.options[b]=c);return d},PhotoApp.authenticate=function(){return(new PhotoApp.Auth).start()},PhotoApp.paginate=function(){return $.ias({container:".thumbnails",item:".photo",pagination:".pagination",next:".next a",loader:'<img src="ias/loader.gif">'})},PhotoApp.Auth=function(){function a(){this.email=PhotoApp.options.currentUser}return a.prototype.start=function(){var a=this;return jQuery(function(){return a.onload()})},a.prototype.onload=function(){var a=this;return this.doc=$(document),this.logoutURL=$("a.logout").attr("href"),this.doc.on("click","a.login",function(a){return a.preventDefault(),navigator.id.request()}),this.doc.on("click","a.logout",function(a){return navigator.id.logout()}),navigator.id.watch({loggedInUser:this.email,onlogin:function(a){return $("#assertion").val(a),$("#login-form").submit()},onlogout:function(){}})},a}(),PhotoApp.Photo=function(){function a(a,b){var c=this;this.page=a,this.el=b,this.deleteShared=__bind(this.deleteShared,this),this["delete"]=__bind(this["delete"],this),this.copy=__bind(this.copy,this),this.share=__bind(this.share,this),this.edit=__bind(this.edit,this),this.doc=this.page.doc,this.csrf=PhotoApp.options.csrf,this.modal=$("#photo-modal"),this.photoID=this.el.attr("data-photo-id"),this.isPublic=this.el.attr("data-is-public"),this.imageURL=this.el.attr("data-image-url"),this.thumbnailURL=this.el.attr("data-thumbnail-url"),this.downloadURL=this.el.attr("data-download-url"),this.deleteURL=this.el.attr("data-delete-url"),this.deleteSharedURL=this.el.attr("data-delete-shared-url"),this.editURL=this.el.attr("data-edit-url"),this.shareURL=this.el.attr("data-share-url"),this.copyURL=this.el.attr("data-copy-url"),this.owner=this.el.attr("data-owner"),this.ownerURL=this.el.attr("data-owner-url"),this.title=this.el.attr("data-title"),this.height=this.el.attr("data-height"),this.width=this.el.attr("data-width"),this.modalTmpl=$("#photo-modal-template").html(),this.shareFieldTmpl=$("#share-field-template").html(),this.render(),this.doc.off("submit","#edit-photo-form"),this.doc.off("submit","#copy-photo-form"),this.doc.off("submit","#share-photo-form"),this.doc.off("click","#photo-modal .share-add-another-btn"),this.doc.off("click","#photo-modal .remove-share-email"),this.doc.off("click","#photo-modal .cancel-btn"),this.doc.off("click","#photo-modal .edit-btn"),this.doc.off("click","#photo-modal .share-btn"),this.doc.off("click","#photo-modal .copy-btn"),this.doc.off("click","#photo-modal .delete-btn"),this.doc.off("click","#photo-modal .delete-shared-btn"),this.doc.off("click","#photo-modal .permalink-btn"),this.doc.off("click","#photo-modal .close-permalink-btn"),this.doc.on("click","#photo-modal .permalink-btn",function(a){return a.preventDefault(),c.hideButtons(),c.isPublic?$("#photo-modal .permalink-container-is-public").show():$("#photo-modal .permalink-container-is-private").show(),$("#photo-modal input.permalink").focus().select()}),this.doc.on("click","#photo-modal .close-permalink-btn",function(a){return a.preventDefault(),$("#photo-modal .permalink-container").hide(),c.showButtons()}),this.doc.on("click","#photo-modal .share-add-another-btn",function(a){var b,d;return a.preventDefault(),d=$("#share-photo-form input[type='text']").length,b=_.template(c.shareFieldTmpl,{numItems:d}),$(a.currentTarget).parent().before(b)}),this.doc.on("click","#photo-modal .remove-share-email",function(a){return a.preventDefault(),$(a.currentTarget).closest("dd").remove()}),this.doc.on("click","#photo-modal .cancel-btn",function(a){return a.preventDefault(),c.showDefaultContent()}),this.doc.on("submit","#share-photo-form",function(a){return a.preventDefault(),c.submitForm($("#share-photo-form"))}),this.doc.on("submit","#copy-photo-form",function(a){return a.preventDefault(),c.modal.modal("hide"),c.submitForm($("#copy-photo-form"),function(a){if(a.success!=null)return c.el.parent().remove(),c.showMessage(a.message)})}),this.doc.on("submit","#edit-photo-form",function(a){return a.preventDefault(),c.submitForm($("#edit-photo-form"),function(a){var b;return c.title=a.title,c.el.attr("data-title",c.title),a.is_public?(c.el.attr("data-is-public","1"),c.isPublic=!0):(c.el.removeAttr("data-is-public"),c.isPublic=!1),b=c.el.find("img"),b.attr("alt",c.title),b.attr("title",c.title),c.modal.find("h3").text(c.title),c.modal.modal("show")})}),this.renderButton("#photo-modal .edit-btn",this.editURL,this.edit),this.renderButton("#photo-modal .share-btn",this.shareURL,this.share),this.renderButton("#photo-modal .copy-btn",this.copyURL,this.copy),this.renderButton("#photo-modal .delete-btn",this.deleteURL,this["delete"]),this.renderButton("#photo-modal .delete-shared-btn",this.deleteSharedURL,this.deleteShared),this.modal.on("show",function(){var a,b,d,e,f;return d=$("#photo-modal .photo-load-progress .bar"),e=0,f=function(){if(e<100)return e+=5,d.width(e+"%")},b=setInterval(f,300),a=new Image,a.src=c.thumbnailURL,a.onload=function(){return clearInterval(b),$("#photo-modal .photo-image").show(),$("#photo-modal .photo-load-progress").hide(),$("#photo-modal-footer").show()}}),this.modal.modal("show")}return a.prototype.render=function(){return this.modal.html(_.template(this.modalTmpl,this))},a.prototype.renderButton=function(a,b,c){var d=this;return b!=null?$(a).show().on("click",function(a){return a.preventDefault(),c(a)}):$(a).hide()},a.prototype.showMessage=function(a){return PhotoApp.showMessage(a,"#photo-modal .messages")},a.prototype.submitForm=function(a,b){var c=this;return $.post(a.attr("action"),a.serialize(),function(a){if(!a.success)return $("#photo-modal-load").html(a.html);a.message!=null&&c.showMessage(a.message),c.showDefaultContent();if(b!=null)return b(a)})},a.prototype.showButtons=function(){return $("#photo-modal-footer .buttons").show()},a.prototype.hideButtons=function(){return $("#photo-modal-footer .buttons").hide()},a.prototype.showDefaultContent=function(){return $("#photo-modal-load").hide(),$("#photo-modal-content").show(),this.showButtons()},a.prototype.showForm=function(a){var b=this;return $("#photo-modal-content").hide(),this.hideButtons(),$.get(a,null,function(a){return $("#photo-modal-load").show().html(a.html)})},a.prototype.edit=function(){return this.showForm(this.editURL)},a.prototype.share=function(){return this.showForm(this.shareURL)},a.prototype.copy=function(){return this.showForm(this.copyURL)},a.prototype["delete"]=function(){return this.deleteAction(this.deleteURL)},a.prototype.deleteShared=function(){return this.deleteAction(this.deleteSharedURL)},a.prototype.deleteAction=function(a){var b=this;if(confirm("Are you sure you want to delete this photo?"))return this.modal.modal("hide"),$.post(a,{csrf_token:this.csrf},function(a){if(a.success!=null)return b.el.parent().remove(),PhotoApp.showMessage("Photo '"+b.title+"' has been deleted")})},a}(),PhotoApp.SharedPage=function(){function a(){var a=this;jQuery(function(){return a.onload()})}return a.prototype.onload=function(){return PhotoApp.paginate()},a}(),PhotoApp.UploadPage=function(){function a(){var a=this;jQuery(function(){return a.onload()})}return a.prototype.onload=function(){var a,b=this;return this.doc=$(document),this.imageFieldTmpl=$("#image-field-template").html(),a=3,$(".upload-add-another-btn").click(function(c){var d,e,f;c.preventDefault(),d=$(c.currentTarget),f=$("form input[type='file']").length;if(f<a){e=_.template(b.imageFieldTmpl,{numItems:f}),d.parent().before(e);if(f+1>=a)return d.parent().hide()}}),this.doc.on("click",".remove-upload-field",function(b){var c;b.preventDefault(),$(b.currentTarget).parent().remove(),c=$("form input[type='file']").length;if(c<a)return $(".upload-add-another-btn").parent().show()})},a}(),PhotoApp.PhotosPage=function(){function a(a){var b=this;this.tagsURL=a,this.csrf=PhotoApp.options.csrf,jQuery(function(){return b.onload()})}return a.prototype.loadTags=function(){var a=this;return $("#tag-cloud").remove(),$.get(this.tagsURL,null,function(b){if(b.tags.length>0)return a.searchBox.append(a.tagCloudHtml),$("#tag-cloud").jQCloud(b.tags)})},a.prototype.onload=function(){var a=this;return this.doc=$(document),this.searchBox=$("#search-box"),this.searchBox.hide(),this.searchBtn=$("#search-btn"),this.tagCloudHtml=$("#tag-cloud-template").html(),this.doc.on("click","a.thumbnail",function(b){return b.preventDefault(),new PhotoApp.Photo(a,$(b.currentTarget))}),this.doc.on("click","#search-btn",function(b){var c;b.preventDefault(),a.searchBox.slideToggle("slow"),a.searchBtn.toggleClass("btn-primary"),c=a.searchBtn.find("i"),c.toggleClass("icon-white");if(!a.searchBtn.is(".btn-primary"))return a.loadTags()}),PhotoApp.paginate()},a}();