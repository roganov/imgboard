var ENABLE_LIVE_UPDATES = false;
var LIVE_UPDATEST_URL = 'http://localhost:8001/';

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
    var m = window.location.pathname.match(/^\/(\w+)/);
    return m ? m[1] : null;
}
function getThreadId() {
    'use strict';
    var m = window.location.pathname.match(/^\/\w+\/t\/(\d+)/);
    return m ? m[1] : null;
}