var pics = [];

function moveAnimate(element, newParent){
        var height = element.height();
        var width = element.width();
        var oldOffset = element.offset();
        element.appendTo(newParent);
        var newOffset = element.offset();

        var temp = element.clone().appendTo('body');
        temp    .css('position', 'absolute')
                .css('left', oldOffset.left)
                .css('top', oldOffset.top)
                .css('zIndex', 1000)
                .css('width', width)
                .css('height', height);
        element.hide();
        temp.animate( { 'top': newOffset.top,
                        'left':newOffset.left,
                        'width':element.width(),
                        'height':element.height()}, 'slow', function(){
           element.show();
           temp.remove();
        });
    }

function addImages(container, pics){
    $.each(pics, function(index, value) {
        container.append(
            $(document.createElement("li"))
                .addClass("selector-item")
                .attr({id: 'image_'+index})
                .append(
            $(document.createElement("img"))
                .attr({ src: value['thumbnailLink'], title: 'image ' + index })
                .addClass("thumbnail")
                )
                .append(
            $(document.createElement("div"))
                .addClass("img-controls")
                .html("<i class='icon-remove'></i>")
                )
            );
    });
}

$(function(){
    var $container = $('#profiles_list1');
//    $container.imagesLoaded( function(){
        $container.masonry({
            itemSelector : '.profile-item',
            isAnimated: true,
            isFitWidth: true,
        });
//    });
    $('#profile-pic').tooltip({
        'trigger': 'hover',
        'placement': 'right'
    });
    if ( pics.length == 0 ) { $("#img-selector-1").css('display','none') }
    if ( $("#img-selector-1").length > 0 ){
        addImages($('#selected-list'), pics);
        $( "#selected-list, #trash-1" ).sortable({
                placeholder: 'ui-sortable-placeholder',
                forcePlaceholderSize: true,
                items: 'li',
                connectWith: ".connectedSortable",
                revert: true,
                containment: '#img-selector-1',
                distance: 10,
                activate: function(event, ui) {
                    $("#trash-1").addClass("dropzone")
                },
                deactivate: function(event, ui) {
                    $("#trash-1").removeClass("dropzone")
                },
            }).disableSelection();
        $( ".img-controls" ).click(function() {
            var source = $(this).parents('.connectedSortable');
            if (source.attr('id') == 'selected-list') { var target = '#trash-1'}
            else { var target = '#selected-list'};
            moveAnimate($(this).parent('.selector-item'), target)
        });
        $('form').submit(function(){
            $('#img_data').val($('#selected-list').sortable( "serialize" ));
            return true;
        });
        // $("#add_images").click(function() {
        //     addImages($('#selected-list'), results);
        //     return false;
        // });
    }
});

var timeoutObj;
$(function(){
  // Manual method using timeout, shortcutting the weird behavior of hover,
  // which causes glitching if pointer doesn't go to the popover through the 
  // arrow
  $('.myClassPopover').popover({
    offset: 10,
    trigger: 'manual',
    html: true,
    placement: 'bottom',
    template: '<div class="popover" onmouseover="clearTimeout(timeoutObj);$(this).mouseleave(function() {$(this).hide();});"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
  }).mouseenter(function(e) {
    $(this).popover('show');
  }).mouseleave(function(e) {
    var ref = $(this);
    timeoutObj = setTimeout(function(){
        ref.popover('hide');
    }, 50);
  });
  $('.tooltip-top').tooltip({
    trigger: 'hover',
    placement: 'top',
    animate: true,
    //delay: 500,
  });
    $('.tooltip-right').tooltip({
    trigger: 'hover',
    placement: 'right',
    animate: true,
    //delay: 500,
  });
    $('.tooltip-bottom').tooltip({
    trigger: 'hover',
    placement: 'bottom',
    animate: true,
    //delay: 500,
  });
    $('.tooltip-left').tooltip({
    trigger: 'hover',
    placement: 'left',
    animate: true,
    //delay: 500,
  });

});

// typeahead javascript
$(function() {
    var labels, mapped
    $("#global_search").typeahead({
        source: function (query, process) {
            $.get(URL_TYPEAHEAD, {q: query}, function (data) {
                labels = []
                mapped = {}
                $.each(data, function (i, item) {
                    mapped[item.title] = item
                    labels.push(item.title)
                })
                process(labels)
            })
        },
        updater: function (item) {
            var obj = mapped[item];
            $('#obj_class').val(obj.class);
            $('#obj_id').val(obj.id);
            return obj.title
        }
    });
});

// select2 tags default parameters
var select2TagsParameters = {
  placeholder: TAG_PLACEHOLDER,
  multiple:true,
  minimumInputLength: 2,
  tokenSeparators: [","],
  initSelection: function (element, callback) {
      // reload tags
      var data = [];
      $(element.val().split(/, ?/)).each(function () {
          data.push({id: this, text: this});
      });
      callback(data);
  },
  createSearchChoice: function(term, data) {
      if ($(data).filter(function() { return this.text.localeCompare(term)===0; }).length===0) {
          return {id:term, text:term};
      }
  },
  ajax: {
    url: URL_REDIS_TAG,
    dataType: 'json',
    quietMillis: 100,
    data: function (term, page) { // page is the one-based page number tracked by Select2
        return {
            q: term, //search term
            limit: 20, // page size
        };
    },
    results: function (data, page) {
      $.each(data, function(i){
          data[i].id = data[i].name;
          data[i].text = data[i].name;
      });
      // console.log(data);
      var more = (page * 10) < data.total; // whether or not there are more results available
      // notice we return the value of more so Select2 knows if more results can be loaded
      return {results: data, more: more};
    }
  },
  containerCssClass: 'select2-bootstrap',
};
$.extend(select2TagsParameters, select2BaseParameters)

// *** Joyride tutorial ***

function launchJoyride(){
    $("#joyRideContent").joyride({
        'tipContainer': '.navbar',
        postRideCallback: function(){ //seb : it works with and without '' (around 'postRideCallback') : what should we do?
            $('#help-dropdown').tooltip('show');
            setTimeout("$('#help-dropdown').tooltip('hide')", 3000);
        },
    });
};

$('#link-tuto').click(function () {
    launchJoyride();
});

$('.tooltip-help').tooltip({
    trigger: 'manual',
    placement: 'bottom',
});
// *** End of Joyride tutorial ***
