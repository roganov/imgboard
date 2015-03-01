window.onload = function() {
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
    })
};