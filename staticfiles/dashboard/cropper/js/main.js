window.onload = function () {
    'use strict';
    var URL = window.URL || window.webkitURL;
    const request = new Request()
    const csrftoken = getCookie('csrftoken');


    var Cropper = window.Cropper;
    var container = document.querySelector('.img-container');
    var image = container.getElementsByTagName('img').item(0);
    var isUnderstand=document.getElementById("do-u-understand")
    var loading_gif=document.getElementById("loading-gif")
    var cropper = new Cropper(image, options);
    var originalImageURL = image.src;
    var uploadedImageType = 'image/jpeg';
    var uploadedImageName = 'cropped.jpg';
    var uploadedImageURL;
    var is_selected = false;
    var original_image;
    var dimension_ok;


    var options = {
        aspectRatio: 1,
        preview: '.img-preview',
        viewMode: 1,
        ready: function (e) {
            console.log(e.type);
        },
        cropstart: function (e) {
            console.log(e.type, e.detail.action);
        },
        cropmove: function (e) {
            console.log(e.type, e.detail.action);
        },
        cropend: function (e) {
            console.log(e.type, e.detail.action);
        },
        crop: function (e) {
            var data = e.detail;

            console.log(e.type);

        },
        zoom: function (e) {
            console.log(e.type, e.detail.ratio);
        }
    };
    var cropper = new Cropper(image, options);

    var submit_button=document.getElementById("submit-design")
    submit_button.addEventListener("click", submit_design)

    var data = {
        method: "getCroppedCanvas",
        target: null,
        option: {
            "maxWidth": 4096,
            "maxHeight": 4096,
            "fillColor": "#fff"
        }
    }


    var warn = document.getElementById("warn")

    function submit_design(e) {
        if(isUnderstand.checked ){
            var result = cropper[data.method](data.option, data.secondOption);
            var cropped_blob = result.toDataURL(uploadedImageType);
            var reader = new FileReader();
            reader.readAsDataURL(original_image);
            reader.onload = function () {
                submit_to_server(cropped_blob, reader.result)
            };
        }else{
            warn.hidden=false;

        }

    }

    function submit_to_server(cropped_blob,original_blob){
        loading_gif.hidden=false
        submit_button.disabled=true
         request.post(window.location.pathname,
            {
                "cropped_blob": cropped_blob,
                "original_blob" : original_blob,
            }
            , csrftoken)
            .then(data => {
                loading_gif.hidden=true;
                loading_gif.disabled=false;
                window.location=submit_button.getAttribute("url")

            })
            .catch(err => alert("Something went wrong."));
    }

    // Import image
    var inputImage = document.getElementById('inputImage');

    var fake_input = document.getElementById("fake-input")
    fake_input.addEventListener("click", () => {
        inputImage.click();
    })




    if (URL) {

        inputImage.onchange =  function () {


           var files = inputImage.files;
            var file;

            if (files && files.length) {
                file = files[0];

                if (/^image\/\w+/.test(file.type)) {

                     let img = new Image()
            img.src = window.URL.createObjectURL(inputImage.files[0])
            img.onload = () => {
                if(img.height<960 || img.width<960){
                    alert("Invalid dimension! Minimum dimensions of 960px by 960px")
                }else if(img.height>8160 || img.width>2040){
                    alert("Invalid dimension! Maximum dimensions of 2,040px by 8,160px")

                }
                else{
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
                    original_image = inputImage.files[0];
                    inputImage.value = null;
                    document.getElementById("choose_another").hidden = false;
                    document.getElementById("description").hidden = true;
                    submit_button.disabled = false;
                }
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

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }


};


