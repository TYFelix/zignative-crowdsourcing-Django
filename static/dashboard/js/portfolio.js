
const entry_elements=document.getElementsByClassName("logo-element")








const selected_entries=[]

function entryClick(e){
    const element=e

    if(element.classList.contains("logo-selected")){
        element.classList.remove("logo-selected")

        selected_entries.splice(selected_entries.indexOf(element.id),1)
    }else{
        element.classList.add("logo-selected")
        selected_entries.push(element.id)
    }

    console.log(selected_entries)


}

for (var j =0; j< selected_list.length; j++){
    entryClick(document.getElementById(selected_list[j]))
}

function submit_portfolio(){
        request.post('/members/set_portfolio', {"selected":JSON.stringify(selected_entries)}
        , csrftoken)
        .then(data => {
            window.location = "/members/profile"

        })
        .catch(err => alert("Something went wrong."));


}