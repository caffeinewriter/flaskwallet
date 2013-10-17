$(document).ready( function () {
    $('nav .control a').on('click tap', function () {
        $('body').toggleClass('sparse');
        /*
        alert('clickky');
        var el = $(this);
        $.each(el.attr('class').split(/\s+/), function (index, item) {
            if (item != 'toggle') {
            }
        });
        */
        return false;
    });
});
