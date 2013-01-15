$(function() {
    var modalAsk, numberExperts, numberUsers;

    modalAsk = $("#modal-ask");
    $(document).on("click", ".btn-ask", function () {
        var questionId, inputs;
        questionId = $(this).data("question-id");
        $("#question-id", modalAsk).val(questionId);
        modalAsk.modal("show");
    });

    numberExperts = 3;
    $("#id_experts", modalAsk).select2($.extend({}, select2BaseParameters, {
        placeholder: function () {
            var text = ngettext("Select one expert",
                                "Select up to %s experts", numberExperts);
            return interpolate(text, [numberExperts]);
        },
        maximumSelectionSize: numberExperts,
        containerCssClass: 'select2-bootstrap'
    }));

    numberUsers = 3;
    $("#id_users", modalAsk).select2($.extend({}, select2BaseParameters, {
        placeholder: function () {
            var text = ngettext("Select one user",
                                "Select up to %s users", numberUsers);
            return interpolate(text, [numberUsers]);
        },
        multiple: true,
        maximumSelectionSize: numberUsers,
        minimumInputLength: 2,
        tokenSeparators: [","],
        initSelection: function (element, callback) {
            // reload profiles
            var url, ids;
            ids = element.val().split(",");
            url = URL_REDIS_PROFILE + "?id=" + ids.join("&id=");
            console.log(ids);
            return $.ajax({
                url: url,
                dataType: 'json',
            }).done( function (data) { 
                callback(data);
            });
        },
        containerCssClass: 'select2-bootstrap',
        ajax: {
            url: URL_REDIS_PROFILE,
            dataType: 'json',
            quietMillis: 100,
            data: function (term, page) {
                return { q: term, limit: 20 };
            },
            results: function (data, page) {
                var more = (page * 10) < data.total;
                return {results: data, more: more};
            }
        }
    }));
});
