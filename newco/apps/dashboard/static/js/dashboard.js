(function ($) {
    "use strict";
    /*jslint browser:true*/

    var extraOptions = {
        columnWidth: function( containerWidth ) {
            return containerWidth / 2;
        }
    };
    $.triggerMasonry($("#boxes"), ".box", extraOptions);
    $(".collapse").on("shown hidden", function () {
        $.triggerMasonry($("#boxes"), ".box", extraOptions);
        var parentBox = $(this).closest(".box");
        $("button i", parentBox).toggleClass("icon-plus icon-minus");
    });
}(window.jQuery));