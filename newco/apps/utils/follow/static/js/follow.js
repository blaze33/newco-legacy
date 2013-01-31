(function ($) {
    "use strict";
    /*jslint browser:true, devel: true*/

    $(".form-follow").submit(function () {
        $.ajax({
            type: "post",
            data: $(this).serialize() + "&follow",
            success: function(data, textstatus, jqxhr) {
                $("[name=follow]").toggleClass("hidden");
                $.displayMessages(data.messages);
            },
            error: function(xhr, status, error) {
                console.log(xhr, status, error);
            }
        });
        return false;
    });
}(window.jQuery));