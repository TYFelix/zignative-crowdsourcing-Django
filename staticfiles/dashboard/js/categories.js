function liveSearch() {
    var input, filter,  items,groups,  i, j,txtValue,contentValue;
    input = document.getElementById("searchbar");
    filter = input.value.toUpperCase();

    groups = document.getElementsByClassName("category-group");
    for (i = 0; i < groups.length; i++) {
        contentValue = groups[i].textContent || groups[i].innerText;

            if (contentValue.toUpperCase().indexOf(filter) > -1) {
                groups[i].style.display="";

            }

            else {
                groups[i].style.display="none";
            }
        items=groups[i].getElementsByClassName("category-item");
        for(j=0;j<items.length;j++){
            txtValue = items[j].textContent || items[j].innerText;

            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                items[j].style.display="";

            }

            else {
                items[j].style.display="none";
            }
        }

    }
}