/*global jQuery, $, Select2, URL_REDIS_PROFILE*/
/*global ngettext, interpolate*/

function reloadProfiles(element, callback) {
    "use strict";

    // reload profiles
    var url, ids;
    ids = element.val().split(",");
    url = URL_REDIS_PROFILE + "?id=" + ids.join("&id=");
    return jQuery.ajax({
        url: url,
        dataType: "json"
    }).done( function (data) { 
        callback(data);
    });
}

$(function () {
    "use strict";
    /*jslint browser:true */

    var modalAsk, experts, inputExperts, numberExperts, urlExperts,
        numberResults, numberUsers;

    modalAsk = $("#modal-ask");
    $(document).on("click", ".btn-ask", function () {
        var questionId, inputs;
        questionId = $(this).data("question-id");
        $("#question-id", modalAsk).val(questionId);
        modalAsk.modal("show");
    });

    inputExperts = $("#id_experts", modalAsk);
    urlExperts = inputExperts.data("url");
    $.ajax({
        url: urlExperts,
        dataType: "json",
        async: false,
        success: function(data) {
            experts = data;
        } 
    });

    numberExperts = 3;
    inputExperts.select2($.extend({}, $.select2BaseParameters, {
        placeholder: function () {
            var text = ngettext("Select one expert",
                                "Select up to %s experts", numberExperts);
            return interpolate(text, [numberExperts]);
        },
        multiple: true,
        data: experts,
        maximumSelectionSize: numberExperts,
        initSelection: reloadProfiles,
        containerCssClass: "select2-bootstrap",
        formatResultCssClass: function(object) { return "expert"; },
        formatResult: function(result, container, query) {
            var text, markup;
            text = [];
            Select2.util.markMatch(result.text, query.term, text);
            text = text.join("");
            markup = "<img src='" + result.gravatar_url + "'>";
            markup += text + " • <b>" + result.reputation + "</b><br>";
            markup += "<span class='muted'>" + result.about + "</span>";
            return markup;
        }
    }));

    numberUsers = 3;
    numberResults = 5;
    $("#id_users", modalAsk).select2($.extend({}, $.select2BaseParameters, {
        placeholder: function () {
            var text = ngettext("Select one user",
                                "Select up to %s users", numberUsers);
            return interpolate(text, [numberUsers]);
        },
        multiple: true,
        maximumSelectionSize: numberUsers,
        minimumInputLength: 2,
        initSelection: reloadProfiles,
        containerCssClass: "select2-bootstrap",
        ajax: {
            url: URL_REDIS_PROFILE + "?limit=" + numberResults,
            dataType: "json",
            quietMillis: 100,
            data: function (term, page) {
                return { q: term };
            },
            results: function (data, page) { return {results: data}; }
        }
    }));
});
