

function onloadStar(event) {

    for (var i =1;i<5;i++){
        var entries=document.getElementsByClassName("entry_rate"+i)
    Array.from( entries,function(entry){
        var is_read_only=entry.getAttribute("readonly")
        ent = raterJs( {
		starSize:16,
        rating:Number(entry.getAttribute("rating"))  ,
		element:document.querySelector(`#${entry.id}`),
        readOnly:is_read_only,
		rateCallback:function rateCallback(rating, done) {
			this.setRating(rating);
			done();
			const contest_id=   Number( entry.getAttribute("contest_id"))
            const entry_id=Number( entry.getAttribute("entry_id"))

            request.post(`/customer/rate-entry/${contest_id}/${entry_id}`,
            {"rate":Number(rating)},csrftoken)
            .then(data => {


            })
            .catch(err => console.log("errorumuz"+err));
		},
		onLeave: function(currentIndex, currentRating){



        }
	});
    })
    }






}

function reloadStar(){
    onloadStart()
}

window.addEventListener("load", onloadStar, false);


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