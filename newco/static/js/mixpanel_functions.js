$(function() {
    // Affiliation
    $(".click-to-product-row").each(function (index) {
        var product, data;
        product = $(this);
        data = {
            ean: product.data("ean"),
            payload: {
                'product': product.data("name"),
                'store': product.data("store")
            }
        };
        mixpanel.track_links("#" + data.ean, "Click to Product", data.payload);
    });
      
    $(".click-to-product-thumb").each(function (index) {
        var product, data;
        product = $(this);
        data = {
            ean: product.data("ean"),
            payload: {
                'product': product.data("name"),
                'store': product.data("store")
            }
        };
        mixpanel.track_links("#" + data.ean + "-thumb", "Click to Product", data.payload);
    });
    
    $(".click-to-product-drop").each(function (index) {
        var product, data;
        product = $(this);
        data = {
            ean: product.data("ean"),
            payload: {
                'product':product.data("name"),
                'store':product.data("store")
            }
        };
        mixpanel.track_links("#" + data.ean + "-drop", "Click to Product", data.payload);
    });

    // Signup
    if ($('li').hasClass('non_auth')) {
        mixpanel.track("Page Load User non authenticated");
    }
    if ($('li').hasClass('well_auth')) {
        mixpanel.track("Page Load User authenticated");
    }
    mixpanel.track_links("#mixpanel_signup_page","Signup_Page");

    // Homepage
    if ($('div').hasClass('homepage_products')) {
        mixpanel.track("Page Load Homepage Products");
    }
    mixpanel.track_links("#mixpanel_popular","Click Popular");
    mixpanel.track_links("#mixpanel_questions","Click Unanswered Questions");
    mixpanel.track_links("#mixpanel_mynewsfeed","Click My Newsfeed");
    
    //Landing Page
    if ($('li').hasClass('non_auth')){mixpanel.register_once({ 'landing page': window.location.href });};

});
