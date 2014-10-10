var collage = (function() {
    var instantiated = false,
        resizeTimer;
    function resizeCheck(){
        console.log("BEFORE>>> top: " + $("#collage").css("top") + " left: " + $("#collage").css("left") + " width: " + $("#collage").width() + " height: " + $("#collage").height() + " WINDOW("+$(window).width()+","+$(window).height()+")");
        $("#collage").css("left",function() {return ($(window).width()-$(this).width())/2});
        $("#collage").css("top",function() {return ($(window).height()-$(this).height())/2});
        console.log("AFTER>>> top: " + $("#collage").css("top") + " left: " + $("#collage").css("left") + " width: " + $("#collage").width() + " height: " + $("#collage").height() + " WINDOW("+$(window).width()+","+$(window).height()+")");
    }
    function preloadImages() {
        
    }
    function init() {
        $.get('/ajax/collage',{'req':'init'},function(data,textStatus,jqXHR) {
            var cont = $("#collage");
            var M = data.dims[1], N = data.dims[0],m,n;
            var w = cont.width()/M, h =cont.height()/N;
            console.log(M+","+N);
            console.log(w+","+h);
            for (n = 0; n < N; n++) {
                var row = $(document.createElement("div")).addClass("collage-row");
                for (m = 0; m < M; m++) {
                    var img_div = $(document.createElement("div"))
                        .addClass("collage-col")
                        .width(w)
                        .height(h);
                    var img = $(document.createElement("img"))
                        .addClass("collage-img")
                        .attr("src","/static/img/collage/collage"+data.ids[n*M+m]+".jpg")
                        .width(w)
                        .height(h);
                    $(row).append($(img_div).append($(img)));
                }
                $(cont).append(row);
            }
            resizeCheck();
            $(window).resize(function () {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(resizeCheck,100);
            });
        },"json"); 
    }
    function fadeRandom() {
        var new_img = $(document.createElement("img"));
        new_img.load(function() {
            var row = Math.floor(n*Math.random()),
                col = Math.floor(m*Math.random());
            var elm = $("#collage-"+row+"-"+col);
            elm.attr('src',$(this).attr('src'));
        });
        new_img.attr('src','/static/img/test'+Math.floor(10*Math.random())+'.jpg');
    }
    return {
        init:init
    }
}());

$(document).ready(function(){
    collage.init();
});
