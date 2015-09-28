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
        color: 'random-dark',
        fontFamily: 'Times, serif',
        click: function(item) {
            //alert(item[0] + ': ' + category_urls[item[0]]);
            window.location.href=category_urls[item[0]];
        },
    }
    // Update the default value if we are running in a hdppx device
    if (('devicePixelRatio' in window) &&
            window.devicePixelRatio !== 1) {
        devicePixelRatio = window.devicePixelRatio;
    }
    // Set the width and height
    var width = $('#canvas-container').width();
    var height = Math.floor(width * 0.65);
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
