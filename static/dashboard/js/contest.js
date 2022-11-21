const designer_select = document.getElementById("designer_select")
const order_select = document.getElementById("order_select")

designer_select.addEventListener("change", apply_filter)
order_select.addEventListener("change", apply_filter)

const entries_tab = document.getElementById("entries")
const request = new Request()
const csrftoken = getCookie('csrftoken');

const inner_entries = document.getElementById("pills-tabContent")

function decline_entry(e) {
    const entry_id = e.id
    const contest_id = e.getAttribute("contest_id")

    const elements = document.getElementsByClassName("stat_t")
    var active;
    Array.from(elements).forEach(element => {
        if (element.classList.contains("active")) {
            active = element.id
        }
    })

    request.post(`/customer/decline-entry/${contest_id}/${entry_id}`,
        {}, csrftoken)
        .then(data => {
            entries_tab.hidden = true
            entries_tab.innerHTML = data.entries_html

            document.getElementById(active).click()
            entries_tab.hidden = false
            onloadStar();


        })
        .catch(err => console.log("errorumuz" + err));
}


function apply_filter(e) {

    var filter = designer_select.id
    var value = designer_select.value

    var filter2 = order_select.id
    var value2 = order_select.value

    var contest_id = designer_select.getAttribute("contest_id")
    const arg = `${filter}=${value}` +
        `&${filter2}=${value2}`

    var url = `http://${window.location.host}/contest/${contest_id}/apply_filters?${arg}`
    request.get(url)
        .then(data => {

            inner_entries.innerHTML = data.entries_html
            onloadStar();

        })
        .catch(err => console.log(err));

}


function check_or_not(e, entry_id) {
    if (e.classList.contains("rate_checked")) {
    } else {
        for (let i = 1; i < 6; i++) {
            e.getElementById(`{`)
        }
    }
}


const finalists = []
const finalist_names = []
const finalists_object={}

function finalize(e) {
    const entry = e.getAttribute("entry_id")
    const user = e.getAttribute("user")

    const plus = `<span ><i class="fa fa-plus-square mt-2 float-right"></i></span>`
    const cancel = `<span ><i class="fa fa-times-circle text-danger mt-2 float-right"></i></span>`

    if(finalists_object[entry] !== undefined){
        delete finalists_object[entry]

    }else{
        finalists_object[entry]=user;
    }

    var string_object={}

    for(var fin in finalists_object){
        var temp=`entry #${fin}, `
        if(string_object[finalists_object[fin]]==undefined){
            string_object[finalists_object[fin]]=temp;

        }else{
            string_object[finalists_object[fin]]+=temp;

        }
    }

    var main_string = ""

    for(var st in string_object){
        string_object[st]=string_object[st].slice(0,-2)
        main_string+=`${st} (${string_object[st]}), `

    }

    main_string = main_string.slice(0,-2)

    if (finalists.includes(entry)) {
        finalists.pop(entry);
        finalist_names.pop(user);

        e.innerHTML = plus
        if (finalists.length === 0) {

            document.getElementById("confirm_finalist").classList.add("disabled")
        }
    } else {
        if (finalists.length < 5) {
            finalists.push(entry);
            finalist_names.push(user);
            e.innerHTML = cancel
        }
    }

    if (finalists.length > 0) {

        document.getElementById("confirm_finalist").classList.remove("disabled")
    }
    document.getElementById("finalists_text").innerHTML = main_string
}

let winner;

function select_winner(e) {
    const entry = e.getAttribute("entry_id")
    const user = e.getAttribute("user")

    document.getElementById("finalists_text").innerHTML = user


    winner = entry;
    document.getElementById("confirm_winner").classList.remove("disabled")


}

function confirm_finalist(e) {
    if (!e.classList.contains("disabled")) {
        const contest_id = e.getAttribute("contest_id")
        request.post(`/customer/confirm-finalists/${contest_id}`,
            {"finalists": finalists}, csrftoken)
            .then(data => {
                window.location.reload();


            })
            .catch(err => console.log("errorumuz" + err));
    }
}

function confirm_winner(e) {
    if (!e.classList.contains("disabled")) {
        const contest_id = e.getAttribute("contest_id")
        request.post(`/customer/confirm-winner/${contest_id}`,
            {"winner": winner}, csrftoken)
            .then(data => {
                window.location.reload();


            })
            .catch(err => console.log("errorumuz" + err));
    }
}

function add_anouns(e) {
    var url = e.target.getAttribute("url")
    var content = e.target.querySelector("#anouns_textarea").value

    request.post(`${url}`,
        {"content": content}, csrftoken)
        .then(data => {
            document.getElementById("anouns_list").innerHTML = data.anouns_list


        })
        .catch(err => console.log("errorumuz" + err));
    e.target.querySelector("#anouns_textarea").value = ''
    e.preventDefault();
}

function delete_anouns(url) {
    request.delete(`${url}`, csrftoken)
        .then(data => {

            document.getElementById("anouns_list").innerHTML = data.anouns_list

        })
        .catch(err => console.log("errorumuz" + err));
}


// thanks to django documentation :)
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

