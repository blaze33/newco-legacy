// js is ready if we need to do something dynamic

$(function(){
   // $(".one_row").popover({animation:'true', trigger: 'hover', content: 'popover'});
	
    //Affiliation
    $(".mixpanel-product").each(function (index) {
		var product=$(this);
		var data = {
					ean: product.data("ean"),
					payload: {
							  'product':product.data("name"),
							  'store':product.data("store")
							  }
					};
	    mixpanel.track_links("#"+data.ean,"Click to Product", data.payload);
	});
      
    //Signup
    if ($('li').hasClass('non_auth')){mixpanel.track("Page Load User non authenticated");};
    if ($('li').hasClass('well_auth')){mixpanel.track("Page Load User authenticated");};
    mixpanel.track_links("#mixpanel_signup_page","Signup_Page");
    //Homepage
    if ($('div').hasClass('homepage_products')){mixpanel.track("Page Load Homepage Products");};
    mixpanel.track_links("#mixpanel_popular","Click Popular");
	mixpanel.track_links("#mixpanel_questions","Click Unanswered Questions");
	mixpanel.track_links("#mixpanel_mynewsfeed","Click My Newsfeed");
    //Authentification (on Homepage only)
    if ($('li').hasClass('well_auth')){
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
	mixpanel.name_tag(user_name);
    };


});
