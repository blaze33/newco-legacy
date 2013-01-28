/*global displayMessage*/

(function ($) {
    "use strict";
    /*jslint browser:true, devel: true*/

    $(".form-follow").submit(function () {
        console.log("caca");
        $.ajax({
            type: "post",
            data: $(this).serialize() + "&follow",
            success: function(data, textstatus, jqxhr) {
                $("[name=follow]").toggle();
                displayMessage(data.message);
            },
            error: function(xhr, status, error) {
                console.log(xhr, status, error);
            }
        });
        return false;
    });
}(window.jQuery));