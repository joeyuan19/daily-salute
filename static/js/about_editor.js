function preview() {
    $("#poem-preview-title").html(poem["title"]);
    $("#poem-preview-date").html(poem["date"]);
    $("#poem-preview-content").html(poem["poem"]);
    $('#poem-preview-modal').modal();
}

function save() {
    var poem = {
        "about":$("#editor").cleanHtml()
    }
    jQuery.postJSON(window.location.href,poem,function (response) {
        response = eval("("+response+")");
        if (response.status === "success") {
            $("#alert-row").html('<div class="alert alert-success alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><strong>Success!</strong> '+response.msg+'</div>');
        } else if (response.status == "redirect") {
            window.location.href= response.url;
        }
    });
}
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
