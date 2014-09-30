function save() {
    var type;
    if ($("#published").is(":checked")) {
        type = "poem";
    } else {
        type = "draft";
    }
    var poem = {
        "poem":$("#editor").cleanHtml(),
        "title":$("#poem-title").val(),
        "date":$("#poem-date").val(),
        "type":type
    }
    jQuery.postJSON(window.location.href,poem,console.log);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        success: function(response) {
        }
    });
};
