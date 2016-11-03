/*global plupload */
/*global qiniu */
function FileProgress(file, targetID) {
    this.fileProgressID = file.id;
    this.file = file;

    this.opacity = 100;
    this.height = 0;
    this.fileProgressWrapper = $('#' + this.fileProgressID);
    if (!this.fileProgressWrapper.length) {
        // <div class="progress">
        //   <div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="20" aria-valuemin="0" aria-valuemax="100" style="width: 20%">
        //     <span class="sr-only">20% Complete</span>
        //   </div>
        // </div>

        this.fileProgressWrapper = $('<div class="row" />');
        var Wrappeer = this.fileProgressWrapper;
        Wrappeer.attr('id', this.fileProgressID).addClass('progressContainer');

        var progressTextCol = $('<div class="col-md-3 col-xs-12" />');
        progressTextCol.addClass('progressName').text(file.name);


        var fileSize = plupload.formatSize(file.size).toUpperCase();
        var progressSizeCol = $('<div class="col-md-2 col-xs-12" />');
        progressSizeCol.addClass("progressFileSize").text(fileSize);

        var progressBarCol = $('<div class="progress-bar-col col-md-5 col-xs-12" />');
        var progressBarBox = $("<div/>");
        progressBarBox.addClass('info');
        var progressBarWrapper = $("<div/>");
        progressBarWrapper.addClass("progress");

        var progressBar = $("<div/>");
        progressBar.addClass("main-progress progress-bar progress-bar-info progress-bar-striped")
            .attr('role', 'progressbar')
            .attr('aria-valuemax', 100)
            .attr('aria-valuenow', 0)
            .attr('aria-valuemin', 0)
            .width('0%');

        var progressBarPercent = $('<span class=sr-only />');
        progressBarPercent.text(fileSize);

        var progressCancelCol = $('<div class="col-md-2 col-xs-12">' +
            '<button type="button" class="btn btn-default progressCancel">' +
            '<span class="glyphicon glyphicon-remove"></span>' +
            '取消</button></div>');

        progressBar.append(progressBarPercent);
        progressBarWrapper.append(progressBar);
        progressBarBox.append(progressBarWrapper);

        var progressBarStatus = $('<div class="status text-center"/>');
        progressBarBox.append(progressBarStatus);
        progressBarCol.append(progressBarBox);

        Wrappeer.append(progressTextCol);
        Wrappeer.append(progressSizeCol);
        Wrappeer.append(progressBarCol);
        Wrappeer.append(progressCancelCol);

        $('#' + targetID).append($('<hr>'));
        $('#' + targetID).append(Wrappeer);
    } else {
        this.reset();
    }

    this.height = this.fileProgressWrapper.offset().top;
    this.setTimer(null);
}

FileProgress.prototype.setTimer = function(timer) {
    this.fileProgressWrapper.FP_TIMER = timer;
};

FileProgress.prototype.getTimer = function(timer) {
    return this.fileProgressWrapper.FP_TIMER || null;
};

FileProgress.prototype.reset = function() {
    this.fileProgressWrapper.attr('class', "row progressContainer");
    this.fileProgressWrapper.find('.main-progress').attr('aria-valuenow', 0).width('0%').find('span').text('');
    this.appear();
};

FileProgress.prototype.setProgress = function(percentage, speed, chunk_size) {
    this.fileProgressWrapper.addClass('active');

    var file = this.file;
    var uploaded = file.loaded;

    var size = plupload.formatSize(uploaded).toUpperCase();
    var formatSpeed = plupload.formatSize(speed).toUpperCase();
    var progressbar = this.fileProgressWrapper.find('.main-progress');
    if (this.fileProgressWrapper.find('.status').text() === '取消上传'){
        return;
    }
    this.fileProgressWrapper.find('.status').text("已上传: " + size + " 上传速度： " + formatSpeed + "/s");
    percentage = parseInt(percentage, 10);
    if (file.status !== plupload.DONE && percentage === 100) {
        percentage = 99;
    }

    progressbar.attr('aria-valuenow', percentage).css('width', percentage + '%');

    this.appear();
};

FileProgress.prototype.setComplete = function(up, info) {
    var progressBarCol = this.fileProgressWrapper.find('.progress-bar-col');

    var res = $.parseJSON(info);
    var url;
    if (res.url) {
        url = res.url;
    } else {
        var domain = up.getOption('domain');
        url = domain + encodeURI(res.key);
    }

    this.fileProgressWrapper.find('.status').hide();
    this.fileProgressWrapper.find('.progressCancel').hide();

    var progressNameCol = this.fileProgressWrapper.find('.progressName');
    var imageView = '?imageView2/1/w/100/h/100';

    var isImage = function(url) {
        var res, suffix = "";
        var imageSuffixes = ["png", "jpg", "jpeg", "gif", "bmp"];
        var suffixMatch = /\.([a-zA-Z0-9]+)(\?|\@|$)/;

        if (!url || !suffixMatch.test(url)) {
            return false;
        }
        res = suffixMatch.exec(url);
        suffix = res[1].toLowerCase();
        for (var i = 0, l = imageSuffixes.length; i < l; i++) {
            if (suffix === imageSuffixes[i]) {
                return true;
            }
        }
        return false;
    };

    var isImg = isImage(url);

    var Wrapper = $('<div class="Wrapper row"/>');
    var imgWrapper = $('<div class="imgWrapper col-md-6"/>');
    var linkWrapper = $('<a class="linkWrapper" target="_blank"/>');
    var showImg = $('<img src="http://qn.njuaplusplus.com/static/photos/images/loading.gif"/>');

    var filename = progressNameCol.text();
    progressNameCol.html(Wrapper);

    if (!isImg) {
        showImg.attr('src', 'http://qn.njuaplusplus.com/static/photos/images/default_file.png');
        Wrapper.addClass('default');

        imgWrapper.append(showImg);
        Wrapper.append(imgWrapper);
    } else {
        linkWrapper.append(showImg);
        imgWrapper.append(linkWrapper);
        Wrapper.append(imgWrapper);

        var img = new Image();
        var origin_url = url;
        if (!/imageView/.test(url)) {
            url += imageView
        }
        $(img).attr('src', url);

        $(img).on('load', function() {
            showImg.attr('src', url);

            linkWrapper.attr('href', origin_url).attr('title', '查看原图');

            var infoWrapper = $('<ul class="image-info-list"/>');

            infoWrapper.append($('<li>' + filename + '</li>'));
            var ie = Qiniu.detectIEVersion();
            if (!(ie && ie <= 9)) {
                var exif = Qiniu.exif(res.key);
                if (exif) {
                    var exifLink = $('<a href="" target="_blank">查看exif</a>');
                    exifLink.attr('href', origin_url + '?exif');
                    infoWrapper.append($('<li/>').append(exifLink));
                }

                var imageInfo = Qiniu.imageInfo(res.key);
                var infoInner = '<li>格式：' + imageInfo.format + '</li>' +
                    '<li>宽度：' + imageInfo.width + 'px</li>' +
                    '<li>高度：' + imageInfo.height + 'px</li>';

                infoWrapper.append($(infoInner));
            }

            progressBarCol.html(infoWrapper);

        }).on('error', function() {
            showImg.attr('src', 'http://qn.njuaplusplus.com/static/photos/images/default_file.png');
            Wrapper.addClass('default');
        });
    }
};
FileProgress.prototype.setError = function() {
    this.fileProgressWrapper.find('div.progress-bar-col').attr('class', 'text-warning');
    this.fileProgressWrapper.find('.progress').css('width', 0).hide();
    this.fileProgressWrapper.find('.progressCancel').hide();
};

FileProgress.prototype.setCancelled = function(manual) {
    var progressContainer = 'row progressContainer';
    if (!manual) {
        progressContainer += ' fail';
    }
    this.fileProgressWrapper.attr('class', progressContainer);
    this.fileProgressWrapper.find('.progress').remove();
    this.fileProgressWrapper.find('.progressCancel').hide();
};

FileProgress.prototype.setStatus = function(status, isUploading) {
    if (!isUploading) {
        this.fileProgressWrapper.find('.status').text(status).attr('class', 'status text-left');
    }
};

// 绑定取消上传事件
FileProgress.prototype.bindUploadCancel = function(up) {
    var self = this;
    if (up) {
        self.fileProgressWrapper.find('.progressCancel').on('click', function(){
            self.setCancelled(false);
            self.setStatus("取消上传");
            self.fileProgressWrapper.find('.status').css('left', '0');
            up.removeFile(self.file);
        });
    }

};

FileProgress.prototype.appear = function() {
    if (this.getTimer() !== null) {
        clearTimeout(this.getTimer());
        this.setTimer(null);
    }

    if (this.fileProgressWrapper[0].filters) {
        try {
            this.fileProgressWrapper[0].filters.item("DXImageTransform.Microsoft.Alpha").opacity = 100;
        } catch (e) {
            // If it is not set initially, the browser will throw an error.  This will set it if it is not set yet.
            this.fileProgressWrapper.css('filter', "progid:DXImageTransform.Microsoft.Alpha(opacity=100)");
        }
    } else {
        this.fileProgressWrapper.css('opacity', 1);
    }

    this.fileProgressWrapper.css('height', '');

    this.height = this.fileProgressWrapper.offset().top;
    this.opacity = 100;
    this.fileProgressWrapper.show();

};
