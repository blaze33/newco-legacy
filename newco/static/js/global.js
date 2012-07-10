$(function(){
    var $container = $('#profiles_list1');
//    $container.imagesLoaded( function(){
        $container.masonry({
            itemSelector : '.profile-item',
            isAnimated: true,
            isFitWidth: true,
        });
//    });
    $('#profile-pic').tooltip({
        'trigger': 'hover',
        'placement': 'right',
    })
});
