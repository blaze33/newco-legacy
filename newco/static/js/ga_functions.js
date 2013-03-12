

-
-$(document).ready( function() {


-    // add an event to all "Click to Product" links for google analytics
    $(".click-to-product-thumb").click(function () {
		var product=$(this);
		var data = {
					product:product.data("name"),
					store:product.data("store")
					};
        var lab = data.product;
        category = 'Click to Product';
-       _gaq.push(['_trackEvent', category, 'clicked', lab]);
       
    });
    
    $(".click-to-product-row").click(function () {
		var product=$(this);
		var data = {
					product:product.data("name"),
					store:product.data("store")
					};
        var lab = data.product;
        category = 'Click to Product';
-       _gaq.push(['_trackEvent', category, 'clicked', lab]);
       
    });
    
    $(".click-to-product-drop").click(function () {
		var product=$(this);
		var data = {
					product:product.data("name"),
					store:product.data("store")
					};
        var lab = data.product;
        category = 'Click to Product';
-       _gaq.push(['_trackEvent', category, 'clicked', lab]);
       
    });
  
});
