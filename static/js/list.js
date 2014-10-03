var link = function(url) {
    window.location.href = url;
};

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
            callback(response);
        }
    });
};
var moveModal = function(id) {
    $("#move-modal-original-id").val(id);
    $("#move-modal-new-id").val("");
    $('#move-modal').modal();
}
var move = function() {
    var id1 = $("#move-modal-original-id").val();
    var id2 = $("#move-modal-new-id").val();
    var move = {"from":id1,"to":id2};
    console.log(move);
    jQuery.postJSON(window.location.href,move,function(response) {
        response = eval("("+response+")")
        window.location.href='/admin/list/poems/'+response.page;
    });
};
