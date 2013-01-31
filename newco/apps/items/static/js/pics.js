(function ($) {
    "use strict";
    /*jslint browser:true*/

    function moveAnimate(element, newParent) {
        var height, width, oldOffset, newOffset, temp, postions;
        height = element.height();
        width = element.width();
        oldOffset = element.offset();
        element.appendTo(newParent);
        newOffset = element.offset();

        temp = element.clone().appendTo('body');
        temp    .css('position', 'absolute')
                .css('left', oldOffset.left)
                .css('top', oldOffset.top)
                .css('zIndex', 1000)
                .css('width', width)
                .css('height', height);
        element.hide();
        postions = {
            'top': newOffset.top,
            'left':newOffset.left,
            'width':element.width(),
            'height':element.height()
        };
        temp.animate(postions, 'slow', function() {
            element.show();
            temp.remove();
        });
    }

    function addImages(container, pics) {
        $.each(pics, function(index, value) {
            container.append(
                    $("<li>").addClass("selector-item")
                             .attr("id", "image_" + index)
                .append(
                    $("<img>").addClass("thumbnail")
                              .attr({
                                  src: value.thumbnailLink,
                                  title: 'Image ' + index 
                              })
                ).append(
                    $("<div>").addClass("img-controls")
                              .html("<i class='icon-remove'></i>")
                )
            );
        });
    }

    $.picsHandler = function(pics, tableSelector, listSelector, trashSelector, resultSelector) {
        $(tableSelector).toggle(pics.length !== 0);
        if ( $(tableSelector).length > 0 ) {
            addImages($(listSelector), pics);
            $([listSelector, trashSelector].join(", ")).sortable({
                placeholder: 'ui-sortable-placeholder',
                forcePlaceholderSize: true,
                items: 'li',
                connectWith: ".connectedSortable",
                revert: true,
                containment: tableSelector,
                distance: 10,
                activate: function(event, ui) {
                    $(trashSelector).addClass("dropzone");
                },
                deactivate: function(event, ui) {
                    $(trashSelector).removeClass("dropzone");
                }
            }).disableSelection();

            $(".img-controls").click(function () {
                var source, target;
                source = $(this).closest(".connectedSortable");
                if ("#" + source.attr("id") === listSelector) {
                    target = trashSelector;
                } else {
                    target = listSelector;
                }
                moveAnimate($(this).parent('.selector-item'), target);
            });

            var form = $(tableSelector).closest("form");
            form.submit(function () {
                $(resultSelector).val( $(listSelector).sortable("serialize") );
                return true;
            });
        }
    };

}(window.jQuery));
