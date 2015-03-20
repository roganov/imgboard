var NewPosts = (function() {
    'use strict';
    var threadBody = $('.thread'),
        threadOp = threadBody.find('.thread-op'),
        boardSlug = getBoardSlug(),
        threadId = getThreadId(),
        modButton = threadOp.find('.js-mod-button'),
        isModerator = modButton.length > 0,
        url = '/api/new-posts/' + boardSlug + '/t/' + threadId,
        latestId = threadBody.find('.post').last().attr('id') || 0;

    var retryIntervals = [1000*10, 1000*60, 1000*60*3, 1000*60*5], // 10 sec, 1 min, 3 min, 5 min
        retryIntervalIndex = 0;

    function fetchNewPosts(single) {
        var params = {
            type: 'get',
            url: url,
            dataType: 'json',
            data: {latest_id: latestId || ''},
            success: function(data) {
                retryIntervalIndex = 0;
                insertPosts(data.posts);
                if (!single) {
                    setTimeout(fetchNewPosts, retryIntervals[0]);
                }
            },
            error: function(xhr) {
                setTimeout(fetchNewPosts, retryIntervals[retryIntervalIndex]);
                if (retryIntervalIndex + 1 < retryIntervals.length) {
                    retryIntervalIndex++;
                }
            }
        };
        $.ajax(params);
    }
    function liveConnect() {
        var xhr = new XMLHttpRequest(),
            params = {'board_slug': boardSlug,
                      'thread_id': threadId},
            query = $.param(params),
            url = LIVE_UPDATEST_URL + '?' + query;
        xhr.open('GET', url);
        xhr.seen = 0;
        xhr.onreadystatechange = function() {
            console.log('STATECHANGE: ' + xhr.readyState);
            if (xhr.readyState === 2) {
                fetchNewPosts(true);
            } else if (xhr.readyState > 2) {
                var data = xhr.responseText.substr(xhr.seen);
                if (data === '') {
                    // disconnect
                    return;
                }
                console.log('DATA: ' + data);
                var message = JSON.parse(data);
                xhr.seen = xhr.responseText.length;
                if (message.type === 'new-posts') {
                    insertPosts(message.posts);
                }
            }
        };
        xhr.send();
    }

    function insertPost(afterThis, post) {
        if (isModerator) {
            var btn = modButton.clone().removeClass('btn-sm').addClass('btn-xs');
            post.find('.post-title').append(btn);
        }
        afterThis.after(post).after(document.createElement('br'));
    }

    function insertPosts(posts) {
        // merge `posts` array into dom
        // the code handles collisions so tha
        // not post occurs twice for some reason
        var i = 0, j = 0,
            len = posts.length,
            domPosts = threadBody.find('.post'),
            domPostsLen = domPosts.length,
            insertAfter,
            dId;
        if (len === 0) {
            return;
        }
        posts = $.map(posts, $);
        posts.reverse();
        domPosts = $.map([].reverse.call(domPosts), $);
        if (domPostsLen > 0) {
            insertAfter = domPosts[0];
            dId = insertAfter.attr('id');
        } else {
            insertAfter = threadOp;
            dId = -1;
        }
        while (i < len) {
            var newPost = posts[i],
                nId = newPost.attr('id');
            if (nId > dId) {
                insertPost(insertAfter, newPost);
                i++;
            } else if (nId === dId) {
                // already inserted
                i++;
            } else {
                j++;
                if (j < domPostsLen) {
                    insertAfter = domPosts[j];
                    dId = insertAfter.attr('id');
                } else {
                    insertAfter = threadOp;
                    dId = -1;
                }
            }

        }
        latestId = posts[0].attr('id');
    }

    return {
        init: function() {
            if (threadId === null || boardSlug === null) {
                return;
            }
            if (ENABLE_LIVE_UPDATES) {
                liveConnect();
            } else {
                setTimeout(fetchNewPosts, retryIntervals[0]);
            }
        }
    };
}());