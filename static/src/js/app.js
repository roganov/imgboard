$(function() {
    "use strict";
    $('.markupPreviewBtn').click(showRenderedMarkup);

    $(".js-datepicker").datepicker();

    attachGallery('.js-img-popup');

    ModeratorModal.init();
    ReplyPopups.init();
    NewPosts.init();
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
// alias to pass as query parameter to the recaptcha service
var initReCaptcha = reCaptcha.init;


var ModeratorModal = {
    init: function() {
        'use strict';
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
            form.modal();
        });
    }
};
