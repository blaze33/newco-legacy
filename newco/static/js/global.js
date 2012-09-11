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

function addImages(container, pics){
    $.each(pics, function(index, value) {
        container.append(
            $(document.createElement("li"))
                .addClass("selector-item")
                .attr({id: 'image_'+index})
                .append(
            $(document.createElement("img"))
                .attr({ src: value['thumbnailLink'], title: 'image ' + index })
                .addClass("thumbnail")
                )
                .append(
            $(document.createElement("div"))
                .addClass("img-controls")
                .html("<i class='icon-remove'></i>")
                )
            );
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
        addImages($('#selected-list'), pics);
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
        // $("#add_images").click(function() {
        //     addImages($('#selected-list'), results);
        //     return false;
        // });
    }
});

$(function(){
  $('.myClassPopover').popover({
    trigger: 'hover',
    placement: 'in bottom',
    animate: true,
    delay: 500,
    //template: '<div class="popover" onmouseover="$(this).mouseleave(function() {$(this).hide(); });"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
  });
  $('[rel="tooltip-top"]').tooltip({
    trigger: 'hover',
    placement: 'top',
    animate: true,
    //delay: 500,
  });
    $('[rel="tooltip-right"]').tooltip({
    trigger: 'hover',
    placement: 'right',
    animate: true,
    //delay: 500,
  });
});
