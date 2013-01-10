// js is ready if we need to do something dynamic
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
    $(document).on("click", ".btn-ask", function () {
        var questionId, modalAsk, inputs;
        questionId = $(this).data("question-id");
        modalAsk = $("#modal-ask");
        inputs = $("input[id^='question-id_']", modalAsk);
        $.each(inputs, function (i, item) {
            $(item).val(questionId);
        });
        modalAsk.modal("show");
    });
});