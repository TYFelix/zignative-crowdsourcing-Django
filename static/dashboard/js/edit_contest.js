const contest_id=`contest_${JSON.parse(document.getElementById("contest_id").textContent)}`




const selected_logos=[]

function logoClick(e){

    const element=this

    if(element.classList.contains("logo-selected")){
        element.classList.remove("logo-selected")
        selected_logos.pop(element.id)
    }else{
        element.classList.add("logo-selected")
        selected_logos.push(element.id)
    }


    storageStuff("selected_logos",selected_logos)
    e.preventDefault()
}



function setDraft(e){
    const value=e.value
    const key=e.id
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





