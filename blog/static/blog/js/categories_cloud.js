jQuery(function($) {
    var $canvasContainer = $('#canvas-container');
    var $canvas = $('#canvas');
    var devicePixelRatio = 1;
    var $nav = $('nav');

    $nav.removeClass('navbar-fixed-top');
    $nav.addClass('navbar-static-top');
    $nav.css('margin-bottom',0);

    $canvas.on('wordclouddrawn', function(evt) {
//        alert(evt.originalEvent.detail.drawn);
//        console.log(evt);
    });

    // Update the default value if we are running in a hdppx device
    if (('devicePixelRatio' in window) &&
            window.devicePixelRatio !== 1) {
        devicePixelRatio = window.devicePixelRatio;
    }

    var $box = $('<div id="box" hidden />');
    $canvasContainer.append($box);
    window.drawBox = function drawBox(item, dimension) {
        if (!dimension) {
            $box.prop('hidden', true);

            return;
        }


        $box.prop('hidden', false);
        $box.css({
            left: dimension.x / devicePixelRatio + 'px',
            top: dimension.y / devicePixelRatio + 'px',
            width: dimension.w / devicePixelRatio + 'px',
            height: dimension.h / devicePixelRatio + 'px'
        });
    };
});

var getHeight = function() {
    var viewportwidth;
    var viewportheight;

    // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight

    if (typeof window.innerWidth != 'undefined')
    {
        viewportwidth = window.innerWidth;
        viewportheight = window.innerHeight;
    }

    // IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)

    else if (typeof document.documentElement != 'undefined'
            && typeof document.documentElement.clientWidth !=
            'undefined' && document.documentElement.clientWidth != 0)
    {
        viewportwidth = document.documentElement.clientWidth;
        viewportheight = document.documentElement.clientHeight;
    }

    // older versions of IE

    else
    {
        viewportwidth = document.getElementsByTagName('body')[0].clientWidth;
        viewportheight = document.getElementsByTagName('body')[0].clientHeight;
    }
    // console.log(viewportwidth + ', ' + viewportheight);
    return viewportheight;
}

var categoriesCloud = function categoriesCloud(category_list, category_urls) {
    var $canvas = $('#canvas');
    var $htmlCanvas = $('#html-canvas');
    var devicePixelRatio = 1;
    // var category_list = jQuery.parseJSON(category_list);
    // var category_urls = jQuery.parseJSON(category_urls);
    options = {
        list : category_list,
        gridSize: 16,
        weightFactor: 16,
        // color: 'random-dark',
        color: '#f0f0c0',
        fontFamily: 'Times, serif',
        click: function(item) {
            //alert(item[0] + ': ' + category_urls[item[0]]);
            window.location.href=category_urls[item[0]];
        },
        backgroundColor: '#1a1a1a',
        hover: window.drawBox
    }
    // Update the default value if we are running in a hdppx device
    if (('devicePixelRatio' in window) &&
            window.devicePixelRatio !== 1) {
        devicePixelRatio = window.devicePixelRatio;
    }
    // Set the width and height
    var width = $('#canvas-container').width();
    // var height = Math.floor(width * 0.65);
    var height = getHeight() - $('nav').outerHeight(false);
    var pixelWidth = width;
    var pixelHeight = height;

    if (devicePixelRatio !== 1) {
        $canvas.css({'width': width + 'px', 'height': height + 'px'});

        pixelWidth *= devicePixelRatio;
        pixelHeight *= devicePixelRatio;
    } else {
        $canvas.css({'width': '', 'height': '' });
    }

    $canvas.attr('width', pixelWidth);
    $canvas.attr('height', pixelHeight);

    $htmlCanvas.css({'width': pixelWidth + 'px', 'height': pixelHeight + 'px'});

    // Set devicePixelRatio options
    if (devicePixelRatio !== 1) {
        if (!('gridSize' in options)) {
            options.gridSize = 8;
        }
        options.gridSize *= devicePixelRatio;

        if (options.origin) {
            if (typeof options.origin[0] == 'number')
                options.origin[0] *= devicePixelRatio;
            if (typeof options.origin[1] == 'number')
                options.origin[1] *= devicePixelRatio;
        }

        if (!('weightFactor' in options)) {
            options.weightFactor = 1;
        }
        if (typeof options.weightFactor == 'function') {
            var origWeightFactor = options.weightFactor;
            options.weightFactor =
                function weightFactorDevicePixelRatioWrap() {
                    return origWeightFactor.apply(this, arguments) * devicePixelRatio;
                };
        } else {
            options.weightFactor *= devicePixelRatio;
        }
    }

    WordCloud([$canvas[0], $htmlCanvas[0]], options);
}
