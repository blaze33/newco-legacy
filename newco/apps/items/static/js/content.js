$(function() {
    $('#modal-gallery').on('load', function () {
        var modalData, context;
        modalData = $(this).data('modal');
        context = $(modalData.$links[modalData.options.index]).data('context');
        $('#modal-gallery .modal-download span').text(context.trim());
        $('#modal-gallery .modal-download').attr('href', context);
    });
});
