/*global gettext*/

(function ($) {
    "use strict";
    /*jslint browser:true, console:true*/

    var radioSelector = ":radio[name=parents]";

    $.showChecked = function () {
        var selectedValue = $(radioSelector + ":checked").val();
        if ( selectedValue ) {
            $("#div_id_" + selectedValue).fadeToggle();
        }
    };

    $.showChecked();
    $(radioSelector).on("click", function (eventObject) {
        $("#div_id_items, #div_id_tags").hide();
        $.showChecked();
    });

    $("#id_tags").select2($.select2TagsParameters);
    $("#id_item-tags").select2($.select2TagsParameters);

    $.addProduct = function (term) {
        $("#id_items, #id_tags").select2("close");
        $("#id_item-name").val(term);
        $('#itemModal').modal('show');
    };

    $("#id_items").select2($.extend({}, $.select2BaseParameters, {
        placeholder: gettext("Search for a product"),
        // maximumSelectionSize: "{{ form.max_products }}",
        formatNoMatches: function (term) {
            var text, title, button;
            text = $("<span>").append($("<b>").text(term)[0].outerHTML + " " + gettext("not found"));
            title = gettext("Click here if you cannot find the product you want to link your question to.");
            button = $("<button>").addClass("btn").attr({
                title: title,
                onClick: "$.addProduct(\'" + term + "\')"
            }).append($("<i>").addClass("icon-plus")[0].outerHTML + " " + gettext("Create product"));
            return [text[0].outerHTML, button[0].outerHTML].join(" ");
        },
        containerCssClass: "select2-bootstrap"
    }));

    $(function() {
        $("#add-item").on("click", function (eventObject) {
            event.preventDefault();
            $('#itemModal').modal('hide');
            $.ajax({
                type: "post",
                data: $("#itemModal form").serialize() + '&add_item',
                success: function(data, status, xhr) {
                    $("#id_items").append(
                        $("<option>").val(data.id).text(data.name)
                    ).select2(
                        "val", [].concat($("#id_items").val(), [String(data.id)])
                    );
                    $("input[name='next']").val(data.next);
                    $.displayMessages(data.messages);
                }
            });
            return false;
        });
    });
}(window.jQuery));