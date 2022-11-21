

const request = new Request()
const csrftoken = getCookie('csrftoken');

function addComment(e) {
    var url = e.target.getAttribute("url")
    var content = e.target.querySelector("#feedback_textarea").value
    var type = e.target.getAttribute("typ")

    request.post(`${url}`,
        {"content": content,"typ":type}
        , csrftoken)
        .then(data => {
            document.getElementById("comment_block").innerHTML = data.comment_list


        })
        .catch(err => console.log("errorumuz" + err));
    e.target.querySelector("#feedback_textarea").value='';
    e.preventDefault();

}


function getReplyForm(e) {
    const for_attr = e.getAttribute("for")
    const targetDiv = document.getElementById(for_attr)

    targetDiv.querySelector(".reply_form").addEventListener("submit", addReply)

    const isHidden = targetDiv.querySelector(".reply_form").hidden
    targetDiv.querySelector(".reply_form").hidden = !isHidden;

}


function addReply(e) {

    var url = e.target.getAttribute("url")
    var content = e.target.querySelector(".form-control").value
    var type = e.target.getAttribute("typ")
    var for_what = e.target.getAttribute("for")

     request.post(`${url}`,
        {"content": content,"typ":type,"for_what":for_what}
        , csrftoken)
        .then(data => {
            document.getElementById("comment_block").innerHTML = data.comment_list


        })
        .catch(err => console.log("errorumuz" + err));

    e.preventDefault();

}

function deleteComment(url) {
    request.delete(`${url}`, csrftoken)
    .then(data => {
        document.getElementById("comment_block").innerHTML = data.comment_list

    })
    .catch(err => console.log("errorumuz" + err));
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