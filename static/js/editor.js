function preview() {
    var poem = {
        "poem":$("#editor").cleanHtml(),
        "title":$("#poem-title").val(),
        "date":$("#poem-date").val(),
    };
    if (poem["title"].length === 0) {
        poem["title"] = poem["date"];
        poem["date"] = "";
    }
    $("#poem-preview-title").html(poem["title"]);
    $("#poem-preview-date").html(poem["date"]);
    $("#poem-preview-content").html(poem["poem"]);
    $('#poem-preview-modal').modal();
}

function publish() {
    save("poem");
}
function unpublish() {
    save("draft");
}
function promptDelete() {
    $("#delete-modal").modal();
}
function toggleRawHTML() {
    if ($("#raw-html").hasClass('active')) {
        $(".editor-btn").removeClass("disabled");
        $("#raw-html").removeClass('active btn-primary');
        $("#raw-html").addClass('btn-default');
        $("#editor").html($("#editor").text());
    } else {
        $(".editor-btn").addClass("disabled");
        $("#raw-html").addClass('active btn-primary');
        $("#raw-html").removeClass('btn-default');
        $("#editor").text($("#editor").cleanHtml());
    }
}
function save() {
    var type;
    if (window.location.href.indexOf("poem") > 0) {
        type = "poem";
    } else {
        type = "draft";
    }
    save(type);
}
function autosave() {
    console.log("Autosave");
    var content = $("#editor").cleanHtml();
    if (window.lastState===content || content.length === 0) {
        // pass
    } else {
        save();
        window.lastState = $("#editor").cleanHtml();
        var time = new Date();
        $("#auto-save-info").text("Autosaved at "+time.getHours()+":"+time.getMinutes()+":"+time.getSeconds()+" "+time.getMonth()+"/"+time.getDay()+"/"+time.getFullYear());
    }
    setTimeout(function(){autosave();},5*1000);
}
function save(type) {
    var content = "";
    if ($("#raw-html").hasClass('active'))
        content = $.parseHTML($("#editor").cleanHtml())[0].wholeText;
    else {
        content = $("#editor").cleanHtml();
    }
    var poem = {
        "poem":content,
        "title":$("#poem-title").val(),
        "date":$("#poem-date").val(),
        "type":type
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

function deletePoem() {
    jQuery.deleteJSON(window.location.href,{"confirm":"delete"},function (response) {
        window.location.href = '/admin/manage/poems'
    })
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

jQuery.deleteJSON = function(url, args, callback) {
    $.ajax({
        url: url,
        type: "DELETE",
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("_xsrf"));
        },
        success: function(response) {
            callback(response);
        }
    });
};
jQuery.postJSON = function(url, args, callback) {
    args._xsrf = getCookie("_xsrf");
    $.ajax({url: url, data: $.param(args), dataType: "text", type: "POST",
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("_xsrf"));
        },
        success: function(response) {
            callback(response);
        }
    });
};
