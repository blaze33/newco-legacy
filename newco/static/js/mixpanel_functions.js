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

    // Authentification (on Homepage only)
    if ($('li').hasClass('well_auth')) {
        // Pretty sure a loop could narrow down this part to 3 lines of code
        var identity, user_id, user_email, user_created, user_name, user_bio, user_reputation;
        identity = document.getElementById("mixpanel_identity");
        user_id = identity.getAttribute("data-user_id");
        user_email = identity.getAttribute("data-email");
        user_created = identity.getAttribute("data-created");
        user_name = identity.getAttribute("data-name");
        user_bio = identity.getAttribute("data-bio");
        user_reputation = identity.getAttribute("data-reputation");
        mixpanel.people.identify(user_id);
        mixpanel.people.set({
            "email": user_email, "created": user_created, "name": user_name, "bio": user_bio, "reputation": user_reputation
        });
        mixpanel.name_tag(user_name);
    }
});
