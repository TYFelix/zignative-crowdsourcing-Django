
const logo_elements=document.getElementsByClassName("logo-element")
const logo_elements1=document.getElementsByClassName("logo-element1")
const contest_id=`contest_${JSON.parse(document.getElementById("contest_id").textContent)}`
const form_fields=JSON.parse(document.getElementById("form_fields").textContent)

if(!localStorage.getItem(contest_id)){

        if(form_fields!=="{}"){
            for (const [key, value] of Object.entries(form_fields)) {
            storageStuff(key,value)
        }
        fillData()
        }

}

for (var i = 0; i < logo_elements.length; i++) {
    logo_elements[i].addEventListener('click', logoClick, false);
}for (var i = 0; i < logo_elements1.length; i++) {
    logo_elements1[i].addEventListener('click', sizeClick, false);
}


const selected_logos=[]
let selected_sizes=[]
function logoClick(e){

    const element=this

    if(element.classList.contains("logo-selected")){
        element.classList.remove("logo-selected")
        selected_logos.splice(selected_logos.indexOf(element.id),1)
    }else{
        element.classList.add("logo-selected")
        selected_logos.push(element.id)
    }

    if(element.classList.contains("font")){
        storageStuff("selected_fonts",selected_logos)
    }else if(element.classList.contains("sizes")){
        storageStuff("selected_sizes",selected_logos)
    }
    else if(element.classList.contains("socialmedia")){
        storageStuff("selected_socialmedia",selected_logos)
    }else if(element.classList.contains("urls")){
        storageStuff("selected_urls",selected_logos)
    }else if(element.classList.contains("platforms")){
        storageStuff("selected_platforms",selected_logos)
    }else if(element.classList.contains("positions")){
        storageStuff("selected_positions",selected_logos)
    }
    else{
        storageStuff("selected_logos",selected_logos)
    }

    e.preventDefault()
}
function sizeClick(e){
    const element=this

    if(element.classList.contains("logo-selected")){
        element.classList.remove("logo-selected")

        selected_sizes.splice(selected_sizes.indexOf(element.id),1)
    }else{
        element.classList.add("logo-selected")
        selected_sizes.push(element.id)
    }

    storageStuff("selected_screen_sizes",selected_sizes)


    e.preventDefault()
}






function setDraft(e){
    const value=e.value
    const key=e.id
    storageStuff(key,value)
}


function pricePlanClick(e){
    const input=e.getElementsByClassName("plan_check")[0]

    const anotherInputs=document.getElementsByClassName("plan-div")

    Array.from(anotherInputs).forEach(
    function(element, index, array) {
       array[index].classList.remove("price_plan_h")
       array[index].classList.add("price_plan")
       array[index].getElementsByClassName("plan_check")[0].checked=false

    }

);

    if(input.checked){
        input.checked=false
        e.classList.remove("price_plan_h")
        e.classList.add("price_plan")

    }else{
        input.checked=true
        e.classList.remove("price_plan")
        e.classList.add("price_plan_h")
    }

     storageStuff("price_plan",input.id)
     save_as_draft()
}

function featurePlanClick(e){
    const input=e.getElementsByClassName("feature_check")[0]

    const anotherInputs=document.getElementsByClassName("feature-div")



    if(input.checked){
        input.checked=false
        e.classList.remove("price_plan_h")
        e.classList.add("price_plan")

        storageStuff(e.id,false)

    }else{
        input.checked=true
        e.classList.remove("price_plan")
        e.classList.add("price_plan_h")
        storageStuff(e.id,true)
    }


     save_as_draft()
}

function radioClick(e){
    const key = e.name
    const value = e.id
    storageStuff(key,value)
}



function storageStuff(key,value){
    var contest;
    if(localStorage.getItem(contest_id)){
        contest=JSON.parse(localStorage.getItem(contest_id))
    }else{
        var temp={}
        localStorage.setItem(contest_id,JSON.stringify(temp))
        contest=JSON.parse(localStorage.getItem(contest_id))
    }


    contest[key]=value

    localStorage.setItem(contest_id , JSON.stringify(contest));

}



function fillData(){
    if(localStorage.getItem(contest_id)){

        const datas=JSON.parse(localStorage.getItem(contest_id))

        for (const [key, value] of Object.entries(datas)) {
            // var ne= document.getElementById(`${key}`)
            // console.log(ne)
            if (document.getElementById(`${key}`)){
                document.getElementById(`${key}`).value=value
            }
        }




    }
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
const csrftoken = getCookie('csrftoken');


async function postData(url = '', data = {}) {


  const response = await fetch(url,{
        method:"POST",
        body:JSON.stringify(data),
        headers:{
          "Content-Type": "application/json; charset=UTF-8",
            'X-CSRFToken': csrftoken
        }
      })
  return response.json(); // parses JSON response into native JavaScript objects
}








