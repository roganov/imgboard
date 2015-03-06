window.onload = function() {
    // TODO: tidy up the code and use jQuery
    var btns = [].slice.call(document.querySelectorAll('.markupPreviewBtn'));
    var board_slug = window.location.pathname.match(/\/(\w+)\//)[1];
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
        req.send('text='+ encodeURIComponent(text) + '&board_slug=' + board_slug);
    }
    btns.forEach(function(btn) {
        btn.addEventListener('click', handler);
    });

    $(".js-datepicker").datepicker();

    $(".js-action-select").change(function() {
        if (this.value == 'ban') {
            $(".js-action-until").removeClass('hidden');
        }
        else
            $(".js-action-until").addClass('hidden');
    });

    $("body").on('click', '.js-mod-button', function(e) {
        var $this = $(this);
        var parent = $this.closest('.post');
        if (!parent.length) {
            parent = $this.closest('.thread-op');
            if (!parent.length)
                return;
        }
        var id = parent.attr('id');
        $('#content_object').val(id);

        var form = $('#modal-form');
        if (id[0] == 't')
            $(".js-action-select option[value='close'],option[value='pin']").prop('disabled', false);
        else {
            $(".js-action-select option[value='close'],option[value='pin']").prop('disabled', true);
            $(".js-action-select").val('ban');
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
                console.log("mouseout");
                var funRemove = setTimeout(function () {
                    preview.remove()
                }, 1000);
                preview.one('mouseover', function () {
                    clearTimeout(funRemove);
                })
            })
        }
    }).on('mouseout', '.reply', function(e) {
        var leftPreview = $(e.toElement || e.relatedTarget).closest('.post');
        if (!leftPreview.hasClass('preview')) {
        }
    })
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
    replyLink = $(e.target);
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
    if (e.clientY > 0.75*window.innerHeight)
        elem.css({top: '', bottom: window.innerHeight - top + replyLink.height()});
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

    if (hoveredReply.data('parent') == $(this).attr('id'))
        return;

    if (hoveredReply.hasClass('preview')) {
        // if hovered node is another preview
        // we need to removed those previews
        // which are under current
        var funRemove = setTimeout(function () {
            removeAfter(hoveredReply)
        }, 1000);
        // if hovered again, cancel removing
        $(this).one('mouseover', function () {
            clearTimeout(funRemove);
        })
    } else {
        // hovered node is not a preview
        // remove all previews
        var previews = $('.preview');
        var funRemove = setTimeout(function() {
            previews.remove();
        }, 1000);
        previews.mouseenter(function() {
            clearInterval(funRemove);
            previews.mouseenter(null);
        })
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