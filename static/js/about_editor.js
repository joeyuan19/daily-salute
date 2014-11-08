function preview() {
    var content = {
        "about":$("#editor").cleanHtml()
    };
    $("#about-preview-content").html(content["about"]);
    $('#about-preview-modal').modal();
}
function save() {
    var editor_content = "";
    if ($("#raw-html").hasClass('active'))
        editor_content = $.parseHTML($("#editor").cleanHtml())[0].wholeText;
    else {
        editor_content = $("#editor").cleanHtml();
    }
    var content = {
        "about":editor_content,
    }
    jQuery.postJSON(window.location.href,content,function (response) {
        response = eval("("+response+")");
        if (response.status === "success") {
            $("#alert-row").html('<div class="alert alert-success alert-dismissible" role="alert"><button type="button" class="close" data-dismiss="alert"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><strong>Success!</strong> '+response.msg+'</div>');
        } else if (response.status == "redirect") {
            window.location.href= response.url;
        }
    });
}
function toggleRawHTML() {
    if ($("#raw-html").hasClass('active')) {
        $("editor-btn").removeClass('disabled');
        $("#raw-html").removeClass('active btn-primary');
        $("#raw-html").addClass('btn-default');
        $("#editor").html($("#editor").text());
    } else {
        $("editor-btn").addClass('disabled');
        $("#raw-html").addClass('active btn-primary');
        $("#raw-html").removeClass('btn-default');
        $("#editor").text($("#editor").cleanHtml());
    }
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
