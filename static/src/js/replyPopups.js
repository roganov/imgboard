var ReplyPopups = (function () {
    'use strict';

    function removeAfter(node) {
        node = $(node);
        if (node && node.hasClass('preview')) {
            node.nextAll().remove();
        } else {
            $('.preview').remove();
        }
    }

    var POSTS_CACHE = Object.create(null);

    function getPreview(replyId, e) {
        var replyLink = $(e.target);
        var left = replyLink.offset().left + replyLink.width() / 2;
        var top = replyLink.offset().top + replyLink.height();
        var elem = $("<div/>")
            .attr('id', 'prev-' + replyId)
            .css({
                position: "absolute",
                'z-index': 999,
                left: left,
                top: top
            }).addClass('post preview')
            .mouseleave(handlePreviewOut);
        if (left > window.innerWidth / 2) {
            elem.css({left: '', right: window.innerWidth - left});
        }
        if (e.clientY > 0.75 * window.innerHeight) {
            elem.css({top: '', bottom: window.innerHeight - top + replyLink.height()});
        }
        var post = $("#" + replyId).html() || POSTS_CACHE[replyId];
        if (post) {
            elem.html(post);
        } else {
            elem.text("Loading...");
            var boardSlug = getBoardSlug();
            $.ajax({
                method: 'GET',
                url: "/api/" + boardSlug + "/preview/" + replyId,
                success: function (data) {
                    var html = $(data).html();
                    elem.html(html);
                    POSTS_CACHE[replyId] = html;
                }
            });
        }
        return elem;
    }

    function handlePreviewOut(e) {
        var hoveredReply = $(e.toElement || e.relatedTarget).closest('.post');

        if (hoveredReply.data('parent') === $(this).attr('id')) {
            return;
        }

        var funRemove;
        if (hoveredReply.hasClass('preview')) {
            // if hovered node is another preview
            // we need to removed those previews
            // which are under current
            funRemove = setTimeout(function () {
                removeAfter(hoveredReply);
            }, 1000);
            // if hovered again, cancel removing
            $(this).one('mouseover', function () {
                clearTimeout(funRemove);
            });
        } else {
            // hovered node is not a preview
            // remove all previews
            var previews = $('.preview');
            funRemove = setTimeout(function () {
                previews.remove();
            }, 1000);
            previews.mouseenter(function () {
                clearInterval(funRemove);
                previews.mouseenter(null);
            });
        }
    }

    function showPreview(e) {
        var $this = $(this);
        var replyId = $this.text().slice(2);  // slicing `>>`
        var currentPost = $this.closest('.post');
        // clear all previews under current one
        removeAfter(currentPost);

        var replyTo = $("#" + replyId);
        if (replyTo.length && isScrolledIntoView(replyTo)) {
            // if replying post is on screen, highlight and exit
            replyTo.toggleClass('highlight');
            $this.one('mouseout', function () {
                replyTo.toggleClass('highlight');
            });
        } else {
            var preview = getPreview(replyId, e).data('parent', currentPost.attr('id'));
            preview.appendTo(document.body);
            // remove preview if current reply link is hovered out
            $this.one('mouseout', function () {
                var funRemove = setTimeout(function () {
                    preview.remove();
                }, 1000);
                preview.one('mouseover', function () {
                    clearTimeout(funRemove);
                });
            });
        }
    }

    return {
        init: function () {
            $(".reply-this").click(function (e) {
                e.preventDefault();
                var replyToId = $(this).parent().parent().attr('id');
                var textarea = $('form textarea');
                textarea.val(textarea.val() + ">>" + replyToId + "\n").focus();
            });

            $("body").on('mouseenter', '.reply', showPreview);
        }
    };

})();


