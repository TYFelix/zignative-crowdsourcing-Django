
window.onload = () =>{
    var price_blocks = document.getElementsByClassName("field-contest_price")

    Array.from(price_blocks).forEach((el) => {
        var temp_inputs = el.getElementsByTagName("input")
        Array.from(temp_inputs).forEach((elem) => {
            if(elem !== undefined){
                elem.addEventListener("change", change_it)
            }
        
        
        });
        
    });




    function change_it(e){
        var el = e.target;
        var parent = el.parentElement.parentElement
        var fee = parent.getElementsByTagName("input")[1].value
        var prize= parent.getElementsByTagName("input")[0].value
        var total = parseFloat(fee) + parseFloat(prize)
        var contest_price = parent.getElementsByClassName("readonly")[0]
        contest_price.innerHTML = total
    }



}