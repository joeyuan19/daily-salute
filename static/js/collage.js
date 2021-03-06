var collage = (function() {
    var instantiated = false, resizeTimer, randomTimer, lim, ids, N, M, h, w;
    function sizing() {
        if ($(window).width() < 500 || $(window).height() < 500) {
            return "small";
        } else if ($(window).width() > 2000 || $(window).height() > 1000) {
            return "large";
        } else {
            return "normal";
        }
    }
    var state;
    function resizeCheck(){
        if (state !== sizing()) {
            init();
            return;
        }
        state = sizing();
        $("#collage").css("left",function() {return ($(window).width()-$(this).width())/2});
        $("#collage").css("top",function() {return ($(window).height()-$(this).height())/2});
    }
    function fadeRandom() {
        if (M*N == lim) {
            return;
        }
        var _ids = [];
        for (var i = 1; i < lim+1; i++) {
            if (ids.indexOf(i) < 0) {
                _ids.push(i);
            }
        }
        var new_id = _ids[Math.floor(Math.random()*_ids.length)];
        var new_img = $(document.createElement("img"))
            .addClass("collage-img")
            .width(w)
            .height(h)
            .css('opacity',0)
            .load(function() {
                var row = Math.floor(N*Math.random()),
                    col = Math.floor(M*Math.random());
                var elm = $("#collage-"+row+"-"+col);
                elm.append($(this));
                var cur_id = "collage-"+row+"-"+col+"-img";
                $("#"+cur_id).attr("id",cur_id+"-temp");
                $(this).attr("id",cur_id);
                $("#"+cur_id+"-temp").animate(
                    {opacity:0},
                    1000,
                    function(){
                        ids[ids.indexOf(parseInt($(this).attr('ds-collage-img-id')))] = new_id;
                        $(this).remove();
                        clearTimeout(randomTimer);
                        randomTimer = setTimeout(fadeRandom,5000);
                    });
                $(this).animate({opacity:1},1000);
            })
            .attr('src','/static/img/collage/collage'+new_id+'.jpg')
            .attr('ds-collage-img-id',new_id);
    }
    function init() {
        $(window).resize(function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(resizeCheck,100);
        });
        $("#collage").empty();
        state = sizing();
        if (state === "small") {
            $("#collage").width(1000).height(500);
        } else if (state === "large") {
            $("#collage").width(4000).height(2000);
        } else {
            $("#collage").width(2000).height(1000);
        }
        $.get('/ajax/collage',{'req':'init','state':state},function(data,textStatus,jqXHR) {
            console.log(data);
            var cont = $("#collage");
            lim = data.lim;
            ids = data.ids;
            M = data.dims[1];
            N = data.dims[0];
            w = cont.width()/M;
            h = cont.height()/N;
            var m,n;
            for (n = 0; n < N; n++) {
                var row = $(document.createElement("div"))
                    .addClass("collage-row")
                    .height(h);
                for (m = 0; m < M; m++) {
                    var img_div = $(document.createElement("div"))
                        .attr("id","collage-"+n+"-"+m)
                        .addClass("collage-col")
                        .width(w)
                        .height(h);
                    var img = $(document.createElement("img"))
                        .attr("id","collage-"+n+"-"+m+"-img")
                        .addClass("collage-img")
                        .width(w)
                        .height(h)
                        .css('opacity',0)
                        .load(function() {
                            $(this).animate({
                                opacity:1
                            },500+2000*Math.random());
                        })
                        .attr('src',"/static/img/collage/collage"+data.ids[n*M+m]+".jpg")
                        .attr('ds-collage-img-id',data.ids[n*M+m]);
                    $(row).append($(img_div).append($(img)));
                }
                $(cont).append(row);
            }
            resizeCheck();
            
            clearTimeout(randomTimer);
            randomTimer = setTimeout(fadeRandom,1000);
        },"json");
    }
    return {
        init:init
    }
}());

$(document).ready(function(){
    collage.init();
});
