function ThumbnailPopup(params) {
    //var selector = params.selector;
    console.log('thumb');
    var selector = params;
    $(document.body).on('click', selector, displayPopup);
}

function displayPopup(e) {
    e.preventDefault();
    var $img = $(document.createElement('img'));
    $img.on('load', function(e) {
        var $img = $(this);
        $img.appendTo(document.body);
        var clientH = $(window).height(),
            clientW = $(window).width(),
            h = $img.height(),
            w = $img.width(),
            rFrame = fitFrame(w, h, clientW, clientH);
        var top = Math.max(0, (clientH - rFrame.height)/2),
            left = Math.max(0, (clientW - rFrame.width)/2);
        $img.css({
            position: 'fixed',
            'z-index': 999,
            top: top,
            left: left,
            'max-height': clientH,
            'max-width': clientW
        });
    });
    $img.click(function(e) {
        $(this).remove();
    });
    $img.attr('src', $(this).attr('href'));
}

function fitFrame(dx, dy, width, height) {
    ratio = Math.max(1, dx/width, dy/height);
    return {width: dx/ratio, height: dy/ratio};
}