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
    $(document).on("click", ".ask-btn", function () {
        var questionId, modalAsk;
        questionId = $(this).data("question-id");
        modalAsk = $("#modal-ask");
        $("#question-id", modalAsk).val(questionId);
        modalAsk.modal("show");
    });
});