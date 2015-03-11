var ThumbnailPopup = (function() {
    function ThumbnailPopup(params) {
        //var selector = params.selector;
        var selector = params;
        $(document.body).on('click', selector, displayImage);
    }


    function displayLoadedImage(e) {
        var $img = $(this);
        $img.appendTo(document.body);
        var clientH = $(window).height(),
            clientW = $(window).width(),
            h = $img.height(),
            w = $img.width(),
            rFrame = fitFrame(w, h, clientW, clientH);
        $img.data('ratio', h/w);
        var top = Math.max(0, (clientH - rFrame.height)/2),
            left = Math.max(0, (clientW - rFrame.width)/2);
        $img.css({
            position: 'fixed',
            'z-index': 999,
            top: top,
            left: left,
            height: rFrame.height,
            width: rFrame.width
        });
    }

    function displayImage(e) {
        e.preventDefault();
        var $img = $(document.createElement('img'));
        $img.on('load', displayLoadedImage);
        $img.click(function(e) {
            $(this).remove();
        });
        $img.on('wheel', scaleImage);
        $img.attr('src', $(this).attr('href'));
    }

    function scaleImage(e) {
        e.preventDefault();
        var $img = $(this);
        var delta = e.originalEvent.deltaY > 0? -20: 20;
        var ratio = $img.data('ratio');
        $img.css({
            top: parseInt($img.css('top'), 10) - ratio*delta/2,
            left: parseInt($img.css('left'), 10) - delta/2,
            height: parseInt($img.css('height'), 10) + ratio*delta,
            width: parseInt($img.css('width'), 10) + delta
        });
    }

    function fitFrame(dx, dy, width, height) {
        var ratio = Math.max(1, dx/width, dy/height);
        return {width: dx/ratio, height: dy/ratio};
    }

    return ThumbnailPopup;
})();
