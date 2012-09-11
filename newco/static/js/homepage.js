

$(function(){
    var $container = $('#contents_list1');
//    $container.imagesLoaded( function(){
        $container.masonry({
            itemSelector : '.content-item',
            isAnimated: true,
            isFitWidth: true,
        });
//    });
    $('#profile-pic').tooltip({
        'trigger': 'hover',
        'placement': 'right'
    });
});
