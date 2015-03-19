var NewPosts = (function() {
    'use strict';
    var threadBody = $('.thread'),
        boardSlug = getBoardSlug(),
        threadId = getThreadId(),
        url = '/api/new-posts/' + boardSlug + '/t/' + threadId,
        latestId = threadBody.find('.post').last().attr('id');

    var retryIntervals = [1000*10, 1000*60, 1000*60*3, 1000*60*5], // 10 sec, 1 min, 3 min, 5 min
        i = 0;
    function fetchNewPosts() {
        $.ajax({
            type: 'get',
            url: url,
            dataType: 'json',
            data: {latest_id: latestId || ''},
            success: function(data) {
                i = 0;
                insertPosts(data.posts);
                setTimeout(fetchNewPosts, retryIntervals[0]);
            },
            error: function(xhr) {
                setTimeout(fetchNewPosts, retryIntervals[i]);
                if (i + 1 < retryIntervals.length) {
                    i++;
                }
            }
        });
    }
    function insertPosts(posts) {
        var i, len, post;
        for (i = 0, len = posts.length; i < len; i++) {
            threadBody.append('<br></br>');
            post = $(posts[i]).appendTo(threadBody);
        }
        if (post) {
            latestId = post.attr('id');
        }
    }

    return {
        init: function() {
            setTimeout(fetchNewPosts, retryIntervals[0]);
        }
    };
}());