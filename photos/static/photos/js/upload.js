/**
 * Created by aplusplus on 24/10/2016.
 */
$(function() {
    var media_root = $('#media-root').val();
    var uploader_username = $('#uploader_username').val();
    var uploader = Qiniu.uploader({
        runtimes: 'html5,flash,html4',
        browse_button: 'pickfiles',
        container: 'container',
        drop_element: 'container',
        max_file_size: '32mb',
        flash_swf_url: 'http://cdn.staticfile.org/plupload/2.1.9/Moxie.swf',
        dragdrop: true,
        chunk_size: '4mb',
        multi_selection: !(mOxie.Env.OS.toLowerCase() === "ios"),
        uptoken_url: $('#uptoken_url').val(),
        // uptoken_func: function(){
        //     var ajax = new XMLHttpRequest();
        //     ajax.open('GET', $('#uptoken_url').val(), false);
        //     ajax.setRequestHeader("If-Modified-Since", "0");
        //     ajax.send();
        //     if (ajax.status === 200) {
        //         var res = JSON.parse(ajax.responseText);
        //         console.log('custom uptoken_func:' + res.uptoken);
        //         return res.uptoken;
        //     } else {
        //         console.log('custom uptoken_func err');
        //         return '';
        //     }
        // },
        filters: {
            prevent_duplicates: true,
            mime_types: [
                {title: "Image files", extensions: "jpg"}
            ]
        },
        domain: $('#domain').val(),
        get_new_uptoken: false,
        // downtoken_url: '/downtoken',
        // unique_names: true,
        // save_key: true,
        x_vars: {
            // 'size': function (up, file) {
            //     var size = file.size;
            //     console.log("set x_vars size: " + size);
            //     return size;
            // },
            // 'date': function(up, file) {
            //     var myDate = new Date();
            //     var year = myDate.getFullYear();
            //     var month = myDate.getMonth() + 1;
            //     var date = myDate.getDate();
            //     if (month < 10) {
            //         month = "0" + month;
            //     }
            //     if (date < 10) {
            //         date = "0" + date;
            //     }
            //     var date = year + "/" + month + "/" + date;
            //     return date;
            // },
            'uploader': function () {
                return uploader_username;
            },
            'filename': function(up, file) {
                return file.name.substring(0, file.name.lastIndexOf('.')).toLowerCase();
            }
        },
        auto_start: true,
        log_level: 5,
        init: {
            'FilesAdded': function (up, files) {
                $('table').show();
                $('#success').hide();
                plupload.each(files, function (file) {
                    var progress = new FileProgress(file, 'fsUploadProgress');
                    progress.setStatus("等待...");
                    progress.bindUploadCancel(up);
                });
            },
            'BeforeUpload': function (up, file) {
                var progress = new FileProgress(file, 'fsUploadProgress');
            },
            'UploadProgress': function (up, file) {
                var progress = new FileProgress(file, 'fsUploadProgress');
                progress.setProgress(file.percent + "%", file.speed);
            },
            'UploadComplete': function () {
                $('#success').show();
            },
            'FileUploaded': function (up, file, info) {
                var progress = new FileProgress(file, 'fsUploadProgress');
                progress.setComplete(up, info);
            },
            'Error': function (up, err, errTip) {
                $('table').show();
                var progress = new FileProgress(err.file, 'fsUploadProgress');
                progress.setError();
                progress.setStatus(errTip);
            }
            ,
            'Key': function(up, file) {
                // var myDate = new Date();
                // var year = myDate.getFullYear();
                // var month = myDate.getMonth() + 1;
                // var date = myDate.getDate();
                // if (month < 10) {
                //     month = '0' + month;
                // }
                // if (date < 10) {
                //     date = '0' + date;
                // }
                var filename = file.name.substring(0, file.name.lastIndexOf('.')).toLowerCase();
                // var key = media_root + '/photos/images/' + year + '/' + month + '/' + date + '/' + filename + '.jpg';
                var key= media_root + '/photos/images/' + uploader_username +  '/' + filename + '.jpg';
                return key;
            }
        }
    });

    uploader.bind('FileUploaded', function () {
        console.log('hello man,a file is uploaded');
    });
    $('#container').on(
        'dragenter',
        function (e) {
            e.preventDefault();
            $('#container').addClass('draging');
            e.stopPropagation();
        }
    ).on('drop', function (e) {
        e.preventDefault();
        $('#container').removeClass('draging');
        e.stopPropagation();
    }).on('dragleave', function (e) {
        e.preventDefault();
        $('#container').removeClass('draging');
        e.stopPropagation();
    }).on('dragover', function (e) {
        e.preventDefault();
        $('#container').addClass('draging');
        e.stopPropagation();
    });

});