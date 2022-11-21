const service_select = document.getElementById("service_select")
const industry_select = document.getElementById("industry_select")
const order_select = document.getElementById("order_select")

service_select.addEventListener("change", apply_filter)
industry_select.addEventListener("change", apply_filter)
order_select.addEventListener("change", apply_filter)

const home_div=document.getElementById("home")


const request = new Request()




let url = new URL(window.location)
let params = new URLSearchParams(url.search);



function apply_filter(e) {
    var status = params.get("filter")
    if(status === null){
        status = "in_progress"
    }

    var filter = service_select.id
    var value = service_select.value

    var filter2 = industry_select.id
    var value2 = industry_select.value

    var filter3=order_select.id
    var value3=order_select.value

    const arg =  `&${filter}=${value}`+
                 `&${filter2}=${value2}`+
                 `&${filter3}=${value3}`

    request.get(`http://${window.location.host}/get_by_filter?filter=${status}${arg}`)
        .then(data => {
            home_div.innerHTML=data.contests_html;


        })
        .catch(err => console.log(err));

}






