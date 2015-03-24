$(function() {
    "use strict";
    var BOARD = /^\/(\w+)(?:\/(\d+))?\/?$/,
        THREAD = /^\/(\w+)\/t\/(\d+)\/?$/,
        reserved = ['about'],
        path = location.pathname,
        m;
    if ((m = BOARD.exec(path))) {
        if (reserved.indexOf(m[1]) > 0) {
            return;
        }
        $('.markupPreviewBtn').click(showRenderedMarkup);
        $(".js-datepicker").datepicker();
        attachGallery('.js-img-popup');
        ModeratorModal.init();
        ReplyPopups.init();
    } else if ((m = THREAD.exec(path))) {
        $('.markupPreviewBtn').click(showRenderedMarkup);
        $(".js-datepicker").datepicker();
        attachGallery('.js-img-popup');
        ModeratorModal.init();
        ReplyPopups.init();
        NewPosts.init();
    }

});

function showRenderedMarkup(e) {
    'use strict';
    e.preventDefault();

    var form = $(this).closest('form');
    var previewDiv = form.find('.markupPreview');
    var text = form.find('textarea').val();
    $.post(
        '/api/markup/',
        {
            'text': text,
            'board_slug': getBoardSlug()
        },
        function(data) {
            previewDiv.css('display', 'block');
            previewDiv.html(data.markup);
        });
}

var reCaptcha = {
    init: function () {
        'use strict';
        if ( /captcha=1/.test(document.cookie) ) {
            var capField = $('.g-recaptcha');
            var form = capField.closest('form');
            grecaptcha.render(capField[0], {
                'sitekey': capField.data('sitekey')
            });
            form.on('submit', function(e) {
                if (grecaptcha.getResponse().length <= 0) {
                    e.preventDefault();
                }
            });
        }
    }
};
// alias to pass as query parameter to the recaptcha service
var initReCaptcha = reCaptcha.init;


var ModeratorModal = {
    init: function() {
        'use strict';
        var form = $('#modal-form'),
            actionSelect = form.find('.js-action-select'),
            selectClosePin = actionSelect.find("option[value='close'],option[value='pin']"),
            actionUntil = form.find('.js-action-until');

        form.submit(function(e){
            if (! actionSelect.val()) {
                e.preventDefault();
                actionSelect.parent().parent().addClass('has-error');
            }
        });

        actionSelect.change(function() {
            if (this.value === 'ban') {
                actionUntil.removeClass('hidden');
            }
            else {
                actionUntil.addClass('hidden');
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

            if (id[0] === 't') {  // if thread
                selectClosePin.prop('disabled', false);
            }
            else {
                selectClosePin.prop('disabled', true);
                actionSelect.val('');
            }
            form.modal();
        });
    }
};
