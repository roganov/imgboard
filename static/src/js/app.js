function getBoardSlug() {
     return window.location.pathname.match(/\/(\w+)\//)[1];
}
window.onload = function() {
    "use strict";
    // TODO: tidy up the code and use jQuery
    var btns = [].slice.call(document.querySelectorAll('.markupPreviewBtn'));
    var boardSlug = getBoardSlug();
    function handler(e) {
        e.preventDefault();

        var form = e.target.form;
        var previewDiv = form.querySelector('.markupPreview');
        var text = form.querySelector('textarea').value;
        var req = new XMLHttpRequest();
        req.open('POST', '/api/markup/');
        req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        req.onload = function() {
            previewDiv.style.display = 'block';
            previewDiv.innerHTML = JSON.parse(this.responseText).markup;
        };
        req.send('text='+ encodeURIComponent(text) + '&board_slug=' + boardSlug);
    }
    btns.forEach(function(btn) {
        btn.addEventListener('click', handler);
    });

    $(".js-datepicker").datepicker();

    $(".js-action-select").change(function() {
        if (this.value === 'ban') {
            $(".js-action-until").removeClass('hidden');
        }
        else {
            $(".js-action-until").addClass('hidden');
        }
    });

    $("body").on('click', '.js-mod-button', function(e) {
        $(".js-action-until").addClass('hidden');
        var $this = $(this);
        var parent = $this.closest('.post');
        if (!parent.length) {
            parent = $this.closest('.thread-op');
            if (!parent.length) {
                return;
            }
        }
        var id = parent.attr('id');
        $('#content_object').val(id);

        var form = $('#modal-form');
        if (id[0] === 't') {
            $(".js-action-select option[value='close'],option[value='pin']").prop('disabled', false);
        }
        else {
            $(".js-action-select option[value='close'],option[value='pin']").prop('disabled', true);
            $(".js-action-select").val('delete');
        }
        $('#modal-form').modal();
    });

    $(".reply-this").click(function(e) {
        e.preventDefault();
        var replyToId = $(this).parent().parent().attr('id');
        var textarea = $('form textarea');
        textarea.val(textarea.val() + ">>" + replyToId + "\n").focus();
    });

    $("body").on('mouseenter', '.reply', function(e) {
        var $this = $(this);
        var replyId = $this.text().slice(2);  // slicing `>>`
        var currentPost = $this.closest('.post');
        // clear all previews under current one
        removeAfter(currentPost);

        var replyTo = $("#" + replyId);
        if (replyTo.length && isScrolledIntoView(replyTo)) {
            // if replying post is on screen, highlight and exit
            replyTo.toggleClass('highlight');
            $this.one('mouseout', function() {
                replyTo.toggleClass('highlight');
            });
        } else {
            var preview = getPreview(replyId, e).data('parent', currentPost.attr('id'));
            preview.appendTo(document.body);
            // remove preview if current reply link is hovered out
            $this.one('mouseout', function() {
                var funRemove = setTimeout(function () {
                    preview.remove();
                }, 1000);
                preview.one('mouseover', function () {
                    clearTimeout(funRemove);
                });
            });
        }
    });

    ThumbnailPopup('.js-img-popup');
};

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
    var left = replyLink.offset().left + replyLink.width()/2;
    var top = replyLink.offset().top + replyLink.height();
    var elem = $("<div/>")
        .attr('id', 'prev-' + replyId)
        .css({position: "absolute",
            'z-index': 999,
            left: left,
            top: top
        }).addClass('post preview')
        .mouseleave(handlePreviewOut);
    if (left > window.innerWidth/2) {
        elem.css({left: '', right: window.innerWidth - left});
    }
    if (e.clientY > 0.75*window.innerHeight) {
        elem.css({top: '', bottom: window.innerHeight - top + replyLink.height()});
    }
    var post = $("#"+replyId).html() || POSTS_CACHE[replyId];
    if (post) {
        elem.html(post);
    } else {
        elem.text("Loading...");
        var boardSlug = window.location.pathname.match(/\/(\w+)\//)[1];
        $.ajax({
            method: 'GET',
            url: "/api/" + boardSlug + "/preview/" + replyId,
            success: function(data) {
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
        funRemove = setTimeout(function() {
            previews.remove();
        }, 1000);
        previews.mouseenter(function() {
            clearInterval(funRemove);
            previews.mouseenter(null);
        });
    }
}
function isScrolledIntoView(elem)
{
    var $elem = $(elem);
    var $window = $(window);

    var docViewTop = $window.scrollTop();
    var docViewBottom = docViewTop + $window.height();

    var elemTop = $elem.offset().top;
    var elemBottom = elemTop + $elem.height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

var reCaptcha = {
    init: function () {
        if (! /captcha=0/.test(document.cookie) ) {
            var capField = $('.g-recaptcha');
            grecaptcha.render(capField[0], {
                'sitekey': capField.data('sitekey')
            });
            var form = capField.closest('form');
            form.on('submit', function(e) {
                if (grecaptcha.getResponse().length <= 0) {
                    e.preventDefault();
                }
            });
        }
    }
};
var initReCaptcha = reCaptcha.init;