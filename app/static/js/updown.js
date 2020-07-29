(function($) {
    window.onscroll = function() {
        var toTop = document.getElementById('go-to-top');
        var oldTop = document.documentElement.scrollTop || document.body.scrollTop;
        var timer;
        toTop.onclick = function() {
            var speed = 10;
            timer = setInterval(function() {
                var top = document.documentElement.scrollTop || document.body.scrollTop;
                var goSpeed = top/50;
                if (goSpeed > speed) {
                    goSpeed = speed;
                } else if (goSpeed < 6) {
                    goSpeed = 6;
                }

                if (top > speed) {
                    if(document.documentElement.scrollTop){
                        top = document.documentElement.scrollTop-=speed;
                    }else{
                        top = document.body.scrollTop-=speed;
                    }
                } else {
                    clearInterval(timer);
                }
            }, 0);
        };

        var newTop = document.documentElement.scrollTop || document.body.scrollTop;
        if (newTop > 100) {
            $("#go-to-top").slideDown(300);
        } else {
            $("#go-to-top").slideUp(300);
        }
        if (newTop > oldTop) {
            clearInterval(timer);
        }
        oldTop = newTop;
    };
})(jQuery)