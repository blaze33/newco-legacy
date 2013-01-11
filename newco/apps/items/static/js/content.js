$(function() {
    $('#modal-gallery').on('load', function () {
        var modalData, context;
        modalData = $(this).data('modal');
        context = $(modalData.$links[modalData.options.index]).data('context');
        $('#modal-gallery .modal-download span').text(context.trim());
        $('#modal-gallery .modal-download').attr('href', context);
    });
});

$(function() {
    var modalAsk, numberUsers;

    modalAsk = $("#modal-ask");
    $(document).on("click", ".btn-ask", function () {
        var questionId, inputs;
        questionId = $(this).data("question-id");
        inputs = $("input[id^='question-id_']", modalAsk);
        $.each(inputs, function (i, item) {
            $(item).val(questionId);
        });
        modalAsk.modal("show");
    });

    numberUsers = 3;
    $("#id_profiles", modalAsk).select2($.extend({}, select2BaseParameters, {
        placeholder: function () {
            var text = ngettext("Select one user",
                                "Select up to %s users", numberUsers);
            return interpolate(text, [numberUsers]);
        },
        multiple: true,
        maximumSelectionSize: numberUsers,
        containerCssClass: 'select2-bootstrap',
        ajax: {
            url: URL_REDIS_PROFILE,
            dataType: 'json',
            quietMillis: 100,
            data: function (term, page) {
                return { q: term, limit: 20 };
            },
            results: function (data, page) {
                $.each(data, function(i) {
                    data[i].text = data[i].name;
                });
                var more = (page * 10) < data.total;
                return {results: data, more: more};
            }
        }
    }));
});