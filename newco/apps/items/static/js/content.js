// js is ready if we need to do something dynamic
$(function(){
    $('#modal-gallery').on('load', function () {
        var modalData = $(this).data('modal');
        var context = $(modalData.$links[modalData.options.index]).data('context');
        $('#modal-gallery .modal-download span').text(context.trim());
        $('#modal-gallery .modal-download').attr('href', context);
    });
});
