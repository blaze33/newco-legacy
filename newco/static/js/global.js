var pics = [];

function moveAnimate(element, newParent){
        var height = element.height();
        var width = element.width();
        var oldOffset = element.offset();
        element.appendTo(newParent);
        var newOffset = element.offset();

        var temp = element.clone().appendTo('body');
        temp    .css('position', 'absolute')
                .css('left', oldOffset.left)
                .css('top', oldOffset.top)
                .css('zIndex', 1000)
                .css('width', width)
                .css('height', height);
        element.hide();
        temp.animate( { 'top': newOffset.top,
                        'left':newOffset.left,
                        'width':element.width(),
                        'height':element.height()}, 'slow', function(){
           element.show();
           temp.remove();
        });
    }

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
        'placement': 'right'
    });
    if ( pics.length == 0 ) { $("#img-selector-1").css('display','none') }
    if ( $("#img-selector-1").length > 0 ){
        $.each(pics, function(index, value) {
            $('#selected-list').append(
                $(document.createElement("li"))
                    .addClass("selector-item")
                    .attr({id: 'image_'+index})
                    .append(
                $(document.createElement("img"))
                    .attr({ src: value['image']['thumbnailLink'], title: 'image ' + index })
                    .addClass("thumbnail")
                    )
                    .append(
                $(document.createElement("div"))
                    .addClass("img-controls")
                    .html("<i class='icon-remove'></i>")
                    )
                );
            });
        $( "#selected-list, #trash-1" ).sortable({
                placeholder: 'ui-sortable-placeholder',
                forcePlaceholderSize: true,
                items: 'li',
                connectWith: ".connectedSortable",
                revert: true,
                containment: '#img-selector-1',
                distance: 10,
                activate: function(event, ui) {
                    $("#trash-1").addClass("dropzone")
                },
                deactivate: function(event, ui) {
                    $("#trash-1").removeClass("dropzone")
                },
            }).disableSelection();
        $( ".img-controls" ).click(function() {
            var source = $(this).parents('.connectedSortable');
            if (source.attr('id') == 'selected-list') { var target = '#trash-1'}
            else { var target = '#selected-list'};
            moveAnimate($(this).parent('.selector-item'), target)
        });
        $('form').submit(function(){
            $('#img_data').val($('#selected-list').sortable( "serialize" ));
            return true;
        });
    }
});
