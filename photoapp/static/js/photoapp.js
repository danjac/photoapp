var PhotoApp;if(typeof PhotoApp=="undefined"||PhotoApp===null)PhotoApp={};PhotoApp.Message=function(){function a(a){this.message=a}return a.prototype.show=function(){var a;return a='        <div class="alert alert-success">            <button type="button" class="close" data-dismiss="alert">&times;</button>            '+this.message+"        </div>",$("#messages").html(a).show()},a}(),PhotoApp.showMessage=function(a){return(new PhotoApp.Message(a)).show()},PhotoApp.paginate=function(){return $.ias({container:".thumbnails",item:".photo",pagination:".pagination",next:".next a",loader:'<img src="ias/loader.gif">'})},PhotoApp.Photo=function(){function a(a,b){var c=this;this.page=a,this.el=b,this.doc=this.page.doc,this.modal=$("#photo-modal"),this.photoID=this.el.attr("data-photo-id"),this.imageURL=this.el.attr("data-image-url"),this.thumbURL=this.el.attr("data-thumbnail-url"),this.sendURL=this.el.attr("data-send-url"),this.deleteURL=this.el.attr("data-delete-url"),this.deleteSharedURL=this.el.attr("data-delete-shared-url"),this.editURL=this.el.attr("data-edit-url"),this.shareURL=this.el.attr("data-share-url"),this.copyURL=this.el.attr("data-copy-url"),this.owner=this.el.attr("data-owner"),this.title=this.el.attr("data-title"),this.height=this.el.attr("data-height"),this.width=this.el.attr("data-width"),this.tmpl=$("#photo-modal-template").html(),this.content=_.template(this.tmpl,{image_url:this.imageURL,thumbnail_url:this.thumbURL,title:this.title,height:this.height,width:this.width,owner:this.owner}),this.doc.on("click","#photo-modal .share-add-another-btn",function(a){var b,c;return a.preventDefault(),c=$("#share-photo-form input[type='text']").length,b='<dd><input type="text" name="emails-'+(c-1)+'">                <a href="#" class="remove-share-email"><i class="icon-remove"></i></a>                </dd>',$(a.currentTarget).parent().before(b)}),this.doc.on("click","#photo-modal .remove-share-email",function(a){return a.preventDefault(),$(a.currentTarget).parent().remove()}),this.doc.on("click","#photo-modal .cancel-btn",function(a){return a.preventDefault(),c.showDefaultContent()}),this.doc.on("submit","#share-photo-form",function(a){return a.preventDefault(),c.submitForm($("#share-photo-form"))}),this.doc.on("submit","#copy-photo-form",function(a){return a.preventDefault(),c.modal.modal("hide"),c.submitForm($("#copy-photo-form"),function(a){if(a.success!=null)return c.el.parent().remove(),PhotoApp.showMessage(a.message)})}),this.doc.on("submit","#send-photo-form",function(a){return a.preventDefault(),c.submitForm($("#send-photo-form"))}),this.doc.on("submit","#edit-photo-form",function(a){return a.preventDefault(),c.submitForm($("#edit-photo-form"),function(a){return b=$("[data-photo-id='"+c.photoID+"']"),b.attr("data-title",a.title),b.find("img").attr("title",a.title),$("#photo-modal h3").text(a.title)})}),this.modal.on("show",function(){var a,b,d,e,f;return c.modal.html(c.content),c.editURL!=null?$("#photo-modal .edit-btn").show().on("click",function(){return c.edit()}):$("#photo-modal .edit-btn").hide(),c.shareURL!=null?$("#photo-modal .share-btn").show().on("click",function(){return c.share()}):$("#photo-modal .share-btn").hide(),c.sendURL!=null?$("#photo-modal .send-btn").show().on("click",function(){return c.send()}):$("#photo-modal .send-btn").hide(),c.copyURL!=null?$("#photo-modal .copy-btn").show().on("click",function(){return c.copy()}):$("#photo-modal .copy-btn").hide(),c.deleteURL!=null?$("#photo-modal .delete-btn").show().on("click",function(){return c["delete"]()}):$("#photo-modal .delete-btn").hide(),c.deleteSharedURL!=null?$("#photo-modal .delete-shared-btn").show().on("click",function(){return c.deleteShared()}):$("#photo-modal .delete-shared-btn").hide(),$("#photo-modal .send-btn").on("click",function(){return c.send()}),d=$("#photo-modal .photo-load-progress .bar"),e=0,f=function(){if(e<100)return e+=5,d.width(e+"%")},b=setInterval(f,300),a=new Image,a.src=c.thumbURL,a.onload=function(){return clearInterval(b),$("#photo-modal .photo-image").show(),$("#photo-modal .photo-load-progress").hide(),$("#photo-modal-footer").show()}}),this.modal.modal("show")}return a.prototype.submitForm=function(a,b){var c=this;return $.post(a.attr("action"),a.serialize(),function(a){if(!a.success)return $("#photo-modal-load").html(a.html);a.message!=null&&PhotoApp.showMessage(a.message),c.showDefaultContent();if(b!=null)return b(a)})},a.prototype.showDefaultContent=function(){return $("#photo-modal-load").hide(),$("#photo-modal-content").show()},a.prototype.showForm=function(a){var b=this;return $("#photo-modal-content").hide(),$.get(a,null,function(a){return $("#photo-modal-load").show().html(a.html)})},a.prototype["delete"]=function(){var a=this;if(confirm("Are you sure you want to delete this photo?"))return this.modal.modal("hide"),$.post(this.deleteURL,null,function(b){if(b.success!=null)return a.el.parent().remove(),PhotoApp.showMessage("Photo '"+a.title+"' has been deleted")})},a.prototype.send=function(){return this.showForm(this.sendURL)},a.prototype.edit=function(){return this.showForm(this.editURL)},a.prototype.share=function(){return this.showForm(this.shareURL)},a.prototype.copy=function(){return this.showForm(this.copyURL)},a.prototype.deleteShared=function(){var a=this;if(confirm("Are you sure you want to delete this photo?"))return this.modal.modal("hide"),$.post(this.deleteSharedURL,null,function(b){if(b.success!=null)return a.el.parent().remove(),PhotoApp.showMessage("Photo '"+a.title+"' has been deleted")})},a}(),PhotoApp.SharedPage=function(){function a(){var a=this;jQuery(function(){return a.onload()})}return a.prototype.onload=function(){return PhotoApp.paginate()},a}(),PhotoApp.PhotosPage=function(){function a(a){var b=this;this.tagsURL=a,jQuery(function(){return b.onload()})}return a.prototype.loadTags=function(){var a=this;return $("#tag-cloud").remove(),$.get(this.tagsURL,null,function(b){var c;if(b.tags)return c='<div class="well" id="tag-cloud" style="height:250px;"></div>',a.searchBox.append(c),$("#tag-cloud").jQCloud(b.tags)})},a.prototype.onload=function(){var a=this;return this.doc=$(document),this.searchBox=$("#search-box"),this.searchBox.hide(),this.searchBtn=$("#search-btn"),this.doc.on("click",".thumbnails a",function(b){return new PhotoApp.Photo(a,$(b.currentTarget))}),this.doc.on("click","#search-btn",function(b){var c;return a.searchBox.slideToggle("slow"),a.searchBtn.toggleClass("btn-primary"),c=a.searchBtn.find("i"),c.toggleClass("icon-white"),a.searchBtn.is(".btn-primary")||a.loadTags(),!1}),PhotoApp.paginate()},a}();