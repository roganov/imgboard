var attachGallery = (function() {
    "use strict";

    var arrowSize = 40;
    var rArrowCSS = {
        position: 'fixed',
        width: 0,
        height: 0,
        right: 0,
        top: $(window).height()/2 - arrowSize,
        'border-top': arrowSize/2 + 'px solid transparent',
        'border-bottom': arrowSize/2 + 'px solid transparent',
        'border-left': arrowSize + 'px solid black'
    };
    var lArrowCSS = {
        position: 'fixed',
        width: 0,
        height: 0,
        left: 0,
        top: $(window).height()/2 - arrowSize,
        'border-top': arrowSize/2 + 'px solid transparent',
        'border-bottom': arrowSize/2 + 'px solid transparent',
        'border-right': arrowSize + 'px solid black'
    };

    function ThumbnailPopup(selector) {
        this.selector = selector;
        var that = this;
        $(document.body).on('click', selector, function(e) {
            e.preventDefault();
            var withArrows = true;
            if (that.$img) {
                that.closeImg();
                withArrows = false;
            }
            that.displayImage($(e.currentTarget), withArrows);
        });
    }

    ThumbnailPopup.prototype.displayImage = function($a, arrows) {
        if (arrows) {
            this.lArrow = $(document.createElement('div'))
                .css(lArrowCSS).appendTo(document.body)
                .click($.proxy(this.displayPrev, this));
            this.rArrow = $(document.createElement('div'))
                .css(rArrowCSS).appendTo(document.body)
                .click($.proxy(this.displayNext, this));
        }
        this.$a = $a;
        var $img = this.$img = $(document.createElement('img'));
        $img.on('load', $.proxy(this.displayLoadedImage, this));
        $img.attr('src', this.$a.attr('href'));
        // draggable must go BEFORE click
        $img.draggable({
            scroll: false
        });
        $img.click($.proxy(this.destroy, this));
        $img.on('wheel', $.proxy(this.scaleImage, this));
    };
    ThumbnailPopup.prototype.displayNext = function(e) {
        this.displayNth(1);
    };
    ThumbnailPopup.prototype.displayPrev = function(e) {
        this.displayNth(-1);
    };
    ThumbnailPopup.prototype.displayNth = function(n) {
        var index = $(this.selector).index(this.$a) + n;
        if (index < 0) {
            return;
        }
        var next = $(this.selector + ":eq(" + index + ")");
        if (next.length) {
            this.closeImg();
            this.displayImage(next);
        }
    };
    ThumbnailPopup.prototype.closeImg = function() {
        this.$img.remove();
        this.$img = null;
    };
    ThumbnailPopup.prototype.displayLoadedImage = function(e) {
        var $img = this.$img;
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
    };

    ThumbnailPopup.prototype.scaleImage = function(e) {
        e.preventDefault();
        var $img = this.$img;
        var delta = e.originalEvent.deltaY > 0? -20: 20;
        var ratio = $img.data('ratio');
        $img.css({
            top: parseInt($img.css('top'), 10) - ratio*delta/2,
            left: parseInt($img.css('left'), 10) - delta/2,
            height: parseInt($img.css('height'), 10) + ratio*delta,
            width: parseInt($img.css('width'), 10) + delta
        });
    };

    ThumbnailPopup.prototype.destroy = function() {
        this.closeImg();
        this.lArrow.remove();
        this.rArrow.remove();
    };

    function fitFrame(dx, dy, width, height) {
        var ratio = Math.max(1, dx/width, dy/height);
        return {width: dx/ratio, height: dy/ratio};
    }

    return function(selector) {return new ThumbnailPopup(selector);};
})();
