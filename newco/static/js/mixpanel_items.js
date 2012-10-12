// js is ready if we need to do something dynamic

$(function(){
   // $(".one_row").popover({animation:'true', trigger: 'hover', content: 'popover'});
	
    mixpanel.track_links("#mp_click_store","Go to Store");
    mixpanel.track_links("#mp_click_price","Go to Product");

});
