const selected_entries = []
var entry_place_i = 1
var step2_button = document.getElementById("step-2-button")
var step1_button = document.getElementById("step-1-button")

var step1_div = document.getElementById("poll_step_1")
var step2_div = document.getElementById("poll_step_2")

var poll_objects_in = document.getElementById("id_poll_objects")
var selected_entries_src = []

function entryClick(e) {
    const element = e


    if (element.classList.contains("logo-selected")) {

        if (selected_entries.length === 8) {
            var temp_lj = document.getElementsByClassName("enough-element")
            for (var j = 0; j < temp_lj.length; j++) {
                temp_lj[j].classList.add("logo-element")
                temp_lj[j].classList.remove("enough-element")


            }

        }

        element.classList.remove("logo-selected")

        var img_in_div = element.getElementsByTagName("img")[0]

        selected_entries.splice(selected_entries.indexOf(element.id), 1)
        selected_entries_src.splice(selected_entries_src.indexOf(img_in_div.src), 1)

        if (selected_entries.length === 0) {
            step2_button.disabled = true
        }

    } else {
        if (selected_entries.length !== 8) {
            element.classList.add("logo-selected")
            selected_entries.push(element.id)

            var img_in_div = element.getElementsByTagName("img")[0]
            selected_entries_src.push(img_in_div.src)

            step2_button.disabled = false
            if (selected_entries.length === 8) {

                var temp_l = document.getElementsByClassName("logo-element")
                for (var i = 0; i < temp_l.length; i++) {
                    if (!temp_l[i].classList.contains("logo-selected")) {
                        temp_l[i].classList.add("enough-element")
                        temp_l[i].classList.remove("logo-element")


                    }

                }
            }

        }
    }

    poll_objects_in.value = selected_entries
    console.log(selected_entries_src)

    var temp_len = selected_entries_src.length
    for (var j = 1; j < 9; j++) {
        var temp_ep = document.getElementById("entry_place_"+j)
        if(j<=temp_len){

            temp_ep.src = selected_entries_src[j-1]
            temp_ep.style.visibility = "visible"

        }
        else{
            temp_ep.src = ""
            temp_ep.style.visibility = "hidden"
        }
    }
}

step1_button.addEventListener("click", (e) => {
    step1_div.hidden = false
    step2_div.hidden = true
})

step2_button.addEventListener("click", (e) => {

    step1_div.hidden = true
    step2_div.hidden = false
})


