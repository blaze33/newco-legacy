$(function() {
    var boxCol = $('div[id^="box_"]');
    $.each(boxCol, function (i, item) {
        var btn_icon = $('[rel=collapse_btn]', item);
        var div = $('[rel=collapse_div]', item);
        div.on('shown', function () {
            btn_icon.removeClass('icon-plus').addClass('icon-minus');
        })
        div.on('hidden', function () {
            btn_icon.removeClass('icon-minus').addClass('icon-plus');
        })
    })
});

function TriggerMasonry_boxes() {
    var $container = $('#boxes_container');
    $container.masonry({
        itemSelector : '.box',
        isAnimated: true,
        // Container is span10 => col = container / 10
        columnWidth: function( containerWidth ) {
            return containerWidth / 10;
        },
    });
}

$(function()    {
    TriggerMasonry_boxes()
    $('[rel=collapse_div]').on('hidden',function() { TriggerMasonry_boxes() });
    $('[rel=collapse_div]').on('shown',function() { TriggerMasonry_boxes() });
});