'use strict';
var URL = window.URL || window.webkitURL;


var Cropper = window.Cropper;
var image = document.getElementById('image');


var uploadedImageType = 'image/jpeg';
var uploadedImageName = 'cropped.jpg';
var uploadedImageURL;
var inputImage = document.getElementById("id_cover_photo")


var options = {
    aspectRatio: 16/9,
    preview: '.img-preview',
    viewMode: 2,
    minContainerHeight: 700,
    minContainerWidth: 750,

};

var cropper = new Cropper(image, options);


var data = {
    method: "getCroppedCanvas",
    target: null,
    option: {
        "maxWidth": 4096,
        "maxHeight": 4096,
        "fillColor": "#fff"
    }
}




function crop_now() {

    var result = cropper[data.method](data.option, data.secondOption);
    var cover_blob = result.toDataURL(uploadedImageType);

    request.post(inputImage.getAttribute("url"),
        {
            "image":cover_blob
        }
        , csrftoken)
        .then(data => {
            console.log(data)
            window.location='/members/profile/'

        })
        .catch(err => alert("Something went wrong."));



}



if (URL) {

    inputImage.onchange = function () {


        var files = inputImage.files;
        var file;

        if (files && files.length) {
            file = files[0];

            if (/^image\/\w+/.test(file.type)) {

                let img = new Image()
                img.src = window.URL.createObjectURL(inputImage.files[0])
                img.onload = () => {

                    uploadedImageType = file.type;
                    uploadedImageName = file.name;

                    if (uploadedImageURL) {
                        URL.revokeObjectURL(uploadedImageURL);
                    }

                    image.src = uploadedImageURL = URL.createObjectURL(file);
                    if (cropper) {
                        cropper.destroy();
                    }

                    cropper = new Cropper(image, options);
                    inputImage.value = null;
                    $("#modal").modal('show');



                }
            } else {
                window.alert('Please choose an image file.');
            }
        }

    };
} else {
    inputImage.disabled = true;
    inputImage.parentNode.className += ' disabled';
}







