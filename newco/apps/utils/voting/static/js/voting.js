/*global displayMessage*/

(function ($) {
    "use strict";
    /*jslint browser:true, devel: true*/

    $("[name^=vote]").click(function (eventObject) {
        var form, btnUp, btnDown, parentDiv;
        eventObject.preventDefault();
        form = $(this).closest("form.vote");
        parentDiv = form.closest("div.vote-controls");
        btnUp = $("[name=vote-up]", form);
        btnDown = $("[name=vote-down]", form);
        $.ajax({
            type: "post",
            data: form.serialize() + "&" + $(this).attr("name") + "=" + $(this).val(),
            statusCode: {
                200: function (data) {
                    if ( data.ok ) {
                        btnUp.val(data.conf.up.value);
                        btnUp.attr("data-vote", data.conf.up.dataVote);
                        btnDown.val(data.conf.down.value);
                        btnDown.attr("data-vote", data.conf.down.dataVote);
                        $(".score", parentDiv).text(data.score.score);
                    }
                    displayMessage(data.message);
                }
            },
            error: function(xhr, status, error) {
                console.log(xhr, status, error);
            }
        });
        return false;
    });
}(window.jQuery));