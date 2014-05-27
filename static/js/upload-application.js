/*
 * jQuery File Upload Plugin JS Example 5.0.2
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2010, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://creativecommons.org/licenses/MIT/
 */

/*jslint nomen: true */
/*global $ */


$(function () {
  'use strict';


  if( $("#fileupload").length > 0 ) {

    window.uploadHelper = {

      disableNext: function(disabled){

        var next_button = $('#next');

        if(disabled){
          next_button.addClass('disabled');
          next_button.text('Busy Uploading...');
          next_button.attr('onclick','return false');
        } else {
          next_button.removeClass('disabled');
          next_button.text('Next');
          next_button.attr('onclick','return true');
        }
      },

      getFileUpload: function(fu){
        return $(fu).data('blueimp-fileupload');
      },

      validate: function(files){
 //       console.log("I'm not validating like I should be!");
        return true;
      }
    };

    $('#fileupload').fileupload({
      autoUpload : true,
      limitConcurrentUploads : 3,
      maxFileSize : 52482800, // 50 megabytes, not all browsers support
      previewMaxWidth: 200,
      previewMaxHeight: 200,
      acceptFileTypes:  /.+$/i, // just take images
      url: '/upload_handler/',
      fileInput : $("#fileinput"),
      uploadTemplate: $('#template-upload'),
      downloadTemplate: $('#template-download'),
      dataType: 'json',
      add: function(e, data){
        Pd.Logger.timestamp('Adding image: ' + data.files[0].name, 5);
        var that = uploadHelper.getFileUpload(this);
        data.isValid = uploadHelper.validate(data.files);

        if(!data.isValid){
          alert('invalid files');
          return;
        }

        data.context = that._renderUpload(data.files)
        .appendTo($(this).find('.files')).each(function () {
          $(this).fadeIn( function() {
            $(this).show();
          });
          /* This is added to isotope below, after canvas has loaded */
        }).data('data', data);

        data.jqXHR = data.submit();

        $('#isocontainer .instructions').hide();
        uploadHelper.disableNext(true);
      },
      send: function (e, data) {
        if (!data.isValid) {
          return false;
        }
        Pd.Logger.timestamp('Sending image: ' + data.files[0].name, 5);
        if (data.context && data.dataType &&
            data.dataType.substr(0, 6) === 'iframe') {
        // Iframe Transport does not support progress events.
        // In lack of an indeterminate progress bar, we set
        // the progress to 100%, showing the full animated bar:
        data.context.find(".progress .bar").css("width", "100%");
        }
      },
      done: function (e, data) {
        var that = uploadHelper.getFileUpload(this);
        if (data.context) {
          data.context.each(function (index) {
            var file = ($.isArray(data.result) &&
                        data.result[index]) || {error: 'emptyResult'};

            if (file.error) {
              // probably wasn't an image file

              // Note that this isn't ever hidden while they are on the 
              // page -- uploads aren't serial, so we have to leave it up.
              $('#upload_error').show();

              // TODO: I can't use 'remove' here cause the jQuery data dies
              // with a null ptr exception. Weird.
              $(this).detach();
            }
            else {
              Pd.Logger.timestamp('Sent image: ' + file.name, 5);
              /******************************/
              /* ballen -- isotope gets upset when I swap the entire
               * element out, so I just swap out the stuff below the parent element */
              var $this = $(this);
              var dl_templ = that._renderDownload([file]);
              var contents = dl_templ.find('.contents');
              var target = $this.find('.contents').get();
              // Don't swap in the element until the replacement image has loaded
              contents.find( '.preview img' ).load( function() {
                var pbar =  $('.bar', target);
                if(pbar){
                  pbar.data('progressbar')._destroy = function(){};
                }
                contents.replaceAll( target );
              });
              /* Since we just swapped out the contents, we'll manually add the uuid
               * from the download template */
              var uuid = dl_templ.attr("uuid");
              $this.attr("uuid", uuid);
              IsoWrapper.picDownloaded($this);
            }

            /* If all the pictures have uuids, that means that they
             * all have been downloaded. If so, let's enable
             * that #next button */
            if( $('.pic_container').length == $('.pic_container[uuid]').length ) {
              uploadHelper.disableNext(false);
            }
            /******************************/
          });
        } else {
          that._renderDownload(data.result)
          .css('display', 'none')
          .appendTo($(this).find('.files'))
          .fadeIn(function () {
            // Fix for IE7 and lower:
            $(this).show();
          });
        }
        updateCartCount();
      },
      // Callback for upload progress events:
      progress: function (e, data) {
        if (data.context) {
          var val = parseInt(data.loaded / data.total * 100, 10);
          data.context.find(".progress .bar").css("width", (val + "%"));
          if(val >= 100) {
            //data.context.find(".progress").fadeOut();
          }
        }
      },
      // Callback for global upload progress events:
      progressall: function (e, data) {
        var val = parseInt(data.loaded / data.total * 100, 10);
        var bar = $('#totalprogress');
      },
      // Callback for uploads start, equivalent to the global ajaxStart event:
      start: function () {
        $(this).find('.fileupload-progressbar')
        .progressbar('value', 0).fadeIn();
      },
      stop: function () {
        $(this).find('.fileupload-progressbar').fadeOut();
      }

    });

    var fuHelpers = {
      _formatFileSize: function (file) {
        if (typeof file.size !== 'number') {
          return '';
        }
        if (file.size >= 1000000000) {
          return (file.size / 1000000000).toFixed(2) + ' GB';
        }
        if (file.size >= 1000000) {
          return (file.size / 1000000).toFixed(2) + ' MB';
        }
        return (file.size / 1000).toFixed(2) + ' KB';
      },
      _sggvGcaleImage: function (img, options) {
        options = options || {};
        var canvas = document.createElement('canvas'),
        scale = Math.min(
          (options.maxWidth || img.width) / img.width,
          (options.maxHeight || img.height) / img.height
        );
        if (scale >= 1) {
          scale = Math.max(
            (options.minWidth || img.width) / img.width,
            (options.minHeight || img.height) / img.height
          );
        }
        img.width = parseInt(img.width * scale, 10);
        img.height = parseInt(img.height * scale, 10);
        if (!options.canvas || !canvas.getContext) {
          return img;
        }
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.getContext('2d')
        .drawImage(img, 0, 0, img.width, img.height);
        return canvas;
      },

      _revokeObjectURL : function (url) {
        var undef = 'undefined',
        urlAPI = (typeof window.revokeObjectURL !== undef && window) ||
          (typeof URL !== undef && URL) ||
          (typeof webkitURL !== undef && webkitURL);
        return urlAPI ? urlAPI.revokeObjectURL(url) : false;
      },

      _createObjectURL : function (file) {
        var undef = 'undefined',
        urlAPI = (typeof window.createObjectURL !== undef && window) ||
          (typeof URL !== undef && URL) ||
          (typeof webkitURL !== undef && webkitURL);
        return urlAPI ? urlAPI.createObjectURL(file) : false;
      },

      _loadImage : function (file, callback, options) {
        var that = this,
        url,
        img;
        if (!options || !options.fileTypes ||
            options.fileTypes.test(file.type)) {
          url = this._createObjectURL(file);
        img = $('<img>').bind('load', function () {
          $(this).unbind('load');
          that._revokeObjectURL(url);
          callback(that._scaleImage(img[0], options));
        }).prop('src', url);
        if (!url) {
          this._loadFile(file, function (url) {
            img.prop('src', url);
          });
        }
        }
      },
      _scaleImage: function (img, options) {
        options = options || {};
        var canvas = document.createElement('canvas'),
        scale = Math.min(
          (options.maxWidth || img.width) / img.width,
          (options.maxHeight || img.height) / img.height
        );
        if (scale >= 1) {
          scale = Math.max(
            (options.minWidth || img.width) / img.width,
            (options.minHeight || img.height) / img.height
          );
        }
        img.width = parseInt(img.width * scale, 10);
        img.height = parseInt(img.height * scale, 10);
        if (!options.canvas || !canvas.getContext) {
          return img;
        }
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.getContext('2d')
        .drawImage(img, 0, 0, img.width, img.height);
        return canvas;
      },

      _downloadTemplateHelper : function (file) {
        file.sizef = this._formatFileSize(file);
        return file;
      },

      _renderDownloadTemplate : function (files) {
        var that = this;
        return $.tmpl(
          this.options.downloadTemplate,
          $.map(files, function (file) {
            return that._downloadTemplateHelper(file);
          })
        );
      },

      _renderDownload : function (files) {
        var tmpl = this._renderDownloadTemplate(files);
        if (!(tmpl instanceof $)) {
          return $();
        }
        tmpl.css('display', 'none');
        tmpl.find('.delete button').button({
          text: false,
          icons: {primary: 'ui-icon-trash'}
        });
        tmpl.find('a').each(this._enableDragToDesktop);
        return tmpl;
      },

      _uploadTemplateHelper : function (file) {
        file.sizef = this._formatFileSize(file);
        return file;
      },

      _renderUploadTemplate : function (files) {
        var that = this;
        return $.tmpl(
          this.options.uploadTemplate,
          $.map(files, function (file) {
            return that._uploadTemplateHelper(file);
          })
        );
      },

      _renderUpload : function (files) {
        var that = this,
        options = this.options,
        tmpl = this._renderUploadTemplate(files);
        if (!(tmpl instanceof $)) {
          return $();
        }
        tmpl.css('display', 'none');
        // .slice(1).remove().end().first() removes all but the first
        // element and selects only the first for the jQuery collection:
        tmpl.find('.progress div').slice(1).remove().end().first()
        .progressbar();
        tmpl.find('.start button').slice(
          this.options.autoUpload ? 0 : 1
        ).remove().end().first()
        .button({
          text: false,
          icons: {primary: 'ui-icon-circle-arrow-e'}
        });
        tmpl.find('.cancel button').slice(1).remove().end().first()
        .button({
          text: false,
          icons: {primary: 'ui-icon-cancel'}
        });
        tmpl.find('.preview').each(function (index, node) {
          that._loadImage(
            files[index],
            function (img) {
              /******************************/
              //$(img).hide().appendTo(node).fadeIn(); ORIGINAL
              // ballen add to isotope here
              $(img).appendTo(node);
              var pic_container = $(node).parents('.pic_container');
              $("#isocontainer").isotope( 'insert', pic_container );
              /******************************/
            },
            {
              maxWidth: options.previewMaxWidth,
              maxHeight: options.previewMaxHeight,
              fileTypes: options.previewFileTypes,
              canvas: options.previewAsCanvas
            }
          );
        });
        return tmpl;
      }
    };
    $.extend($('#fileupload').data('blueimp-fileupload'), fuHelpers);


    // Open download dialogs via iframes,
    // to prevent aborting current uploads: 
    $('#fileupload .files a:not([target^=_blank])').on('click', function (e) {
      e.preventDefault();
      $('<iframe style="display:none;"></iframe>')
      .prop('src', this.href)
      .appendTo('body');
    });
  }
});

