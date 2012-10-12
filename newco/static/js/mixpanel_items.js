// js is ready if we need to do something dynamic

$(function(){
   // $(".one_row").popover({animation:'true', trigger: 'hover', content: 'popover'});
	
    mixpanel.track_links("#mp_click_store","Go to Store");
    mixpanel.track_links("#mp_click_price","Go to Product");
	
	
	//$("#mp_tips_product").click(function(){mixpanel.track("Click Tips Product");});
	//$("#mp_create_product").click(function(){mixpanel.track("Create Product only"); });
	//$("#mp_create_featur").click(function(){mixpanel.track("Create product features",{}, 
	//								function() { $("#form").submit();}); return false;});								
	//$("#mp_create_features").click(function(){
		//var form = function() {
		//$("#form1").submit();
		//}; 	
		//mixpanel.track("Create product features",{action: "edit"}, form()); });
	//mixpanel.track_forms("#form1","Click Store Search", 
	//function(form) { alert(form.id);return { form_type: form.id, key: "value" }; });
	//$("#mp_store_search").click(function(){mixpanel.track("Click Store Search"); });
	//$("#mp_store_search_add").click(function(){mixpanel.track("Add a Store Search"); });
	//$("#mp_update_product").click(function(){mixpanel.track("Update Product"); });
	//$("#mp_answer").click(function(){
		//var form = function() {
		//$("#form_detail").action="#answer_form";
		//$("#form_detail").submit();
		//}; 	
		//mixpanel.track("question detail", {},form());});
	//mixpanel.track_forms("#form_detai","question_detail", 
		//function(form) { return { action:"#answer_form" }; });
});
