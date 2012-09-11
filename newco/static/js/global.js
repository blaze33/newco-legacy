var pics = ['https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcSy4FJAXUIPTAPOOI_90LKada48k-jG_weoFEQg9x1vJiZSpcZuvtnecTU',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcTsoWm0SV9eZC_X1SkCU-dZXzJj1qATXulz95JKFEjcgfaUpRGIJqfQBQ',
 'https://encrypted-tbn1.google.com/images?q=tbn:ANd9GcSqzp08TAr9rmg2CQC50cHbPMGnGrYo4ijy7ZZxBLG0taGQhQf-UiXWMe0S',
 'https://encrypted-tbn1.google.com/images?q=tbn:ANd9GcSdQDXsY7SGEa_AtB2qihOmceL6OWXGjbIEDvoz-8GOYz1AEx3292jOf6C7',
 'https://encrypted-tbn3.google.com/images?q=tbn:ANd9GcTtyVCPM7CtB5A5ViR4-3Td222oKBfTwrifr6NE3qtjQdEZ9N0vWzB5YS8I',
 'https://encrypted-tbn0.google.com/images?q=tbn:ANd9GcQ4LzNRpOB8814DdW-vilDU4fCXa8C3oo8iyPEFY1_b-Y27zCm2iMObqps',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcQHIVb9s077jlYS-uydqU32PnU0ewXnM3NnWJDeKJDU2bpd46yBd2lK8gk',
 'https://encrypted-tbn2.google.com/images?q=tbn:ANd9GcTtduBhXw6EoxIFJeUEDtuw_iVkzp22w5ioMTxrwJ-ALRtP19JC0BwMm7M',
 'https://encrypted-tbn0.google.com/images?q=tbn:ANd9GcSgF9w7qAA4dHl-q8nPAP-3tRWvN6c18H5gLj4nUPucHt9rwHT4e9LqXYQ',
 'https://encrypted-tbn3.google.com/images?q=tbn:ANd9GcRp9kQpfyASqNzZOnIUrtxB8tu6zOM33mv6f5JPkVDOGeHIidNPbReB0Is'];
pics=[];

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
                    .append(
                $(document.createElement("img"))
                    .attr({ src: value, title: 'image ' + index })
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
    $('[rel="tooltip-bottom"]').tooltip({
    trigger: 'hover',
    placement: 'bottom',
    animate: true,
    //delay: 500,
  });
    $('[rel="tooltip-left"]').tooltip({
    trigger: 'hover',
    placement: 'left',
    animate: true,
    //delay: 500,
  });
});

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
    if ( pics.length == 0 ) { $("#img-selector-1").css('display','none') }
    if ( $("#img-selector-1").length > 0 ){
        $.each(pics, function(index, value) {
            $('#selected-list').append(
                $(document.createElement("li"))
                    .addClass("selector-item")
                    .append(
                $(document.createElement("img"))
                    .attr({ src: value, title: 'image ' + index })
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
    }
});
