function isScrolledIntoView(elem) {
    'use strict';
    var $elem = $(elem);
    var $window = $(window);

    var docViewTop = $window.scrollTop();
    var docViewBottom = docViewTop + $window.height();

    var elemTop = $elem.offset().top;
    var elemBottom = elemTop + $elem.height();

    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
}

function getBoardSlug() {
    'use strict';
    return window.location.pathname.match(/\/(\w+)\//)[1];
}