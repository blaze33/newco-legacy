/*global jQuery*/

(function ($) {
	"use strict";

    $("#question-form").on("show hidden", function (eventObject) {
        $("#question-icon").toggleClass("icon-plus icon-remove");
        $("#question-text").toggle();
        if ( eventObject.type === "show" ) { $("#id_question-content").focus(); }
    });
}(jQuery));
