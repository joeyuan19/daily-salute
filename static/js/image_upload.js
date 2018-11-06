

function uploadImage() {
    var img = document.getElementById("poem-image");
    if (img.files.length == 1) {
        var form = new FormData();
        form.append("img", img.files[0]);
        var xhr = new XMLHttpRequest();
        xhr.onload = function() {
            $('#image-status')
        };
        xhr.open("post", "/image_upload", true);
        xhr.send(form);
    }
}

