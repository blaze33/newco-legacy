
$(function(){
    $('#profile-pic').tooltip({
        'trigger': 'hover',
        'placement': 'right'
    });
});

function TriggerMasonry(){
    $('#thumbnails_list').masonry('reload');
}
$(function(){
   // simple example, using all default options unless overridden globally
  $('#thumbnails_list').imagesLoaded(function(){
    $('#thumbnails_list').masonry({
        itemSelector : '.content-item',
        isAnimated: true,
        isFitWidth: true,
    });
  });
  $('div.expandable').expander({
			afterExpand:function() {TriggerMasonry();},
			//Timer to relaunch Masonry after the onCollapse event
			onCollapse:function(byUser) {timeout=setTimeout(TriggerMasonry,500);
			}
 	});
});

var why_NewCo_div = $('#why_NewCo');
var subnav2move = $('.subnav-fixed');
$(function(){

    why_NewCo_div.on('show', function () {
        subnav2move.addClass('subnav-moved');
        $('body').addClass('body-less-padding');
    })

    why_NewCo_div.on('shown', function () {
        // Give time to load for subnav displacement : slow sometimes
        setTimeout("$('.tooltip-tutorial').tooltip('show')", 1500);
    })

    why_NewCo_div.on('hide', function () {
        $('.tooltip-tutorial').tooltip('hide');
    })

    why_NewCo_div.on('hidden', function () {
        subnav2move.removeClass('subnav-moved');
        $('body').removeClass('body-less-padding');
        setTimeout("$('.tooltip-tutorial').tooltip('hide')", 1500); // in case of double click on 'why_NewCo_div'
    })

    $('.tooltip-tutorial').tooltip({
        trigger: 'manual',
        placement: 'top',
        animate: true,
        // delay: 500,
    });

    $('.navbar-fixed-top').addClass('reduced-margin-navbar');

    //"Find products or tags in the search bar... "
    $('.arrow_search_bar_trigger').mouseover(function () {
        $('#arrow_search_bar').removeClass('arrow-search-bar-hidden');
        $('#arrow_search_bar').addClass('arrow-search-bar-shown');
    });
    $('.arrow_search_bar_trigger').mouseout(function () {
        $('#arrow_search_bar').removeClass('arrow-search-bar-shown');
        $('#arrow_search_bar').addClass('arrow-search-bar-hidden');
    });
    $('.arrow_search_bar_trigger').click(function () {
        $('#global_search').focus();
    });

    // "explore NewCo"
    $('#explore').click(function(){
        why_NewCo_div.collapse('hide');
        return false;
    });

    // "build your reputation ..."
    $('#reputation-trigger').mouseover(function () {
        $('#reputation-btn').addClass('btn-glow');
    });

    $('#reputation-trigger').mouseout(function () {
        $('#reputation-btn').removeClass('btn-glow');
    });
});
