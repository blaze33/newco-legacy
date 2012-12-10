

-
-$(document).ready( function() {
-    

    $(".dropdown controls").ready(function () {
		var product=document.getElementById("drop");
	    var lab='[Pageload]:'+product.getAttribute("data-name");
        category = 'Load Item Detail';
-       _gaq.push(['_trackEvent', category, 'pageload',lab]);
       
    });

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
