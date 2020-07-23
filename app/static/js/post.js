(function($) {
    $(function(){
        var x = document.getElementsByTagName("table");
        for(i=0; i<x.length; i++) {
            tab = x[i];
            tab.classList.add("table");
            tab.classList.add("table-bordered");
        }
    });

    $(function(){
        var x = document.getElementsByTagName("p");
        for(i=0; i<x.length; i++) {
            p = x[i];
            p.classList.add("dark-grey-text");
            p.classList.add("article");
        }
    });

    $(function(){
        var x = document.querySelectorAll("h1, h2, h3, h4, h5");
        for(i=0; i<x.length; i++) {
            h = x[i];
            h.classList.add("mt-3");
            h.classList.add("mb-3");
        }
    });

    $(function(){
        var x = $('video').parent();
        for(i=0; i<x.length; i++) {
            p = x[i];
            p.classList.add("text-center");
        }
    });

    $(function(){
        var x = document.getElementsByTagName("video");
        for(i=0; i<x.length; i++) {
            video = x[i];
            video.style.width = "85%";
            video.style.height = "auto";
        }
    });
})(jQuery)