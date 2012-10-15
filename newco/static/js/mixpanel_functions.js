// js is ready if we need to do something dynamic

$(function(){
   // $(".one_row").popover({animation:'true', trigger: 'hover', content: 'popover'});
	
    //Affiliation
    mixpanel.track_links("#mp_click_store","Go to Store");
    mixpanel.track_links("#mp_click_price","Go to Product");
    //Signup
    if ($('li').hasClass('non_auth')){mixpanel.track("Page Load User non authenticated");};
    if ($('div').hasClass('well_auth')){mixpanel.track("Page Load User authenticated");};
    mixpanel.track_links("#mixpanel_signup_page","Signup_Page");
    //Homepage
    mixpanel.track_links("#mixpanel_popular","Click Popular");
	mixpanel.track_links("#mixpanel_last","Click Last Added");
	mixpanel.track_links("#mixpanel_questions","Click Unanswered Questions");
	mixpanel.track_links("#mixpanel_mynewsfeed","Click My Newsfeed");
	mixpanel.track_links("#mixpanel_image","Click Image Homepage");
    mixpanel.track_links("#mixpanel_tag_home","Click Tag Homepage");
    //Authentification (on Homepage only)
    if ($('div').hasClass('well_auth')){
    var identity=document.getElementById("mixpanel_identity");
	var user_id=identity.getAttribute("data-user_id");
	var user_email=identity.getAttribute("data-email");
	var user_created=identity.getAttribute("data-created");
	var user_name=identity.getAttribute("data-name");
	var user_bio=identity.getAttribute("data-bio");
	var user_reputation=identity.getAttribute("data-reputation");
	mixpanel.people.identify(user_id);
	mixpanel.people.set({
		"email":user_email,"created":user_created,"name":user_name,"bio":user_bio,"reputation":user_reputation,
	});
    };


});
