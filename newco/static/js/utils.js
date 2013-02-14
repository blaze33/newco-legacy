function htmlDecode (input) {
    "use strict";
    /*jslint browser:true*/

    var e = document.createElement("div");
    e.innerHTML = input;
    return e.childNodes[0].nodeValue;
}
