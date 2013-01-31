(function ($) {
    "use strict";
    /*jslint browser:true*/

    var extraOptions = {
        columnWidth: function( containerWidth ) {
            return containerWidth / 10;
        }
    };
    $.triggerMasonry($("#boxes"), ".box", extraOptions);
    $(".collapse").on("shown hidden", function () {
        $.triggerMasonry($("#boxes"), ".box", extraOptions);
    });
    $.each($(".box"), function (index, Element) {
        $(".collapse", Element).on("shown hidden", function () {
            $("button i", Element).toggleClass("icon-plus icon-minus");
        });
    });
}(window.jQuery));