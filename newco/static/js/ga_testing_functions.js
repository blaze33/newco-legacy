// js is ready if we need to do something dynamic

$(document).ready( function() {
    
    // add an event to all link for google analytics
    $('a').click(function () {
        // tell analytics to save event
        try {
            var identifier=$(this).attr('id') ;
            var href=$(this).attr('href')
            var label="";
            if ( typeof( identifier ) != 'undefined' ) {
                label=label+'[id]:'+identifier
                category='JSLink'
            }
            if ( typeof( href ) != 'undefined' ) {
                label=label+' [href]:'+href
                if ( href[0] == '#' ) {
                    category='Anchor';
                } else {
                    category='Link';
                }
            }
            _gaq.push(['_trackEvent', category, 'clicked', label]);
            // console.log('[tracked]: ' + category + ' ; clicked ; ' + label );
        }
        catch (err) {
            console.log(err);
        }

         //pause to allow google script to run ((GK : ca a pas l'air de marcher sinon...'))
        var date = new Date();
        var curDate = null;
        do {
            curDate = new Date();
        } while(curDate-date < 300);
    });
   
   
    //Add an event when Submit a form
    $('form').submit(function () {
        // tell analytics to save event
        try {
            var identifier=$(this).attr('action') ;
            var label="";
            if ( typeof( identifier ) != 'undefined' ) {
                label=label+'[action]:'+identifier
                category='FormSubmit'
            }
            _gaq.push(['_trackEvent', category, 'submit', label]);
            // console.log('[tracked]: ' + category + ' ; submit ; ' + label );
        }
        catch (err) {
            console.log(err);
        }
        //pause to allow google script to run ((GK : ca a pas l'air de marcher sinon...'))
        var date = new Date();
        var curDate = null;
        do {
            curDate = new Date();
        } while(curDate-date < 300);
    });
});