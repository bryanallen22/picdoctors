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
      $('#fileupload').fileupload({
          autoUpload : true,
          limitConcurrentUploads : 3,
          maxFileSize : 52482800, // 50 megabytes, not all browsers support
          previewMaxWidth: 200,
          previewMaxHeight: 200,
          acceptFileTypes:  /.+$/i, // just take images
          url: '/upload_handler/',
          fileInput : $("input:file[name='files[]']")
      });

      /*
       * ballen disabled - will we ever want this?
       // Load existing files:
       */
      $.getJSON('/upload_handler/', function (files) {
          var fu = $('#fileupload').data('fileupload');
          fu._adjustMaxNumberOfFiles(-files.length);
          fu._renderDownload(files)
              .appendTo($('#fileupload .files'))
              .fadeIn(function () {
                  // Fix for IE7 and lower:
                  $(this).show();
              });
      });
      //*/

      // Open download dialogs via iframes,
      // to prevent aborting current uploads:
      $('#fileupload .files a:not([target^=_blank])').live('click', function (e) {
          e.preventDefault();
          $('<iframe style="display:none;"></iframe>')
              .prop('src', this.href)
              .appendTo('body');
      });
    }
});
