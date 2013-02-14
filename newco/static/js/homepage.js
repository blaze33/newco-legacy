(function ($) {
    "use strict";
    /*jslint browser:true*/

    $("#why_NewCo").on("show hidden", function (eventObject) {
        $(".subnav-fixed").toggleClass("subnav-moved");
        $("body").toggleClass("body-less-padding");
    });

    $("#why_NewCo").on("shown hide", function (eventObject) {
        $(".tooltip-tutorial").tooltip("toggle");
    });

    $("#arrow-trigger").on({
        hover: function () {
            $('#search-arrow').toggleClass("hidden shown");
        },
        click: function () {
            $('#global_search').focus();
        }
    });

    $("#reputation-trigger").hover(function () {
        $('#reputation-btn').toggleClass("btn-glow");
    });
}(window.jQuery));
