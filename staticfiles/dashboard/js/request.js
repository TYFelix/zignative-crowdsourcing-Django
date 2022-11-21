class Request {
    async get(url){ // Get Request

        const response = await fetch(url); // Response Object
        const data = await response.json() // JSON Object
        return data;
    }
    async post(url,data,csrftoken){
        const response = await fetch(url,{
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                      "Content-type": "application/json; charset=UTF-8; ",
                        'X-CSRFToken': csrftoken

                    }
                }); // Response Object

        const responsedata = await response.json();

        return responsedata;


    }


    async form_post(url,data,csrftoken){
        const response = await fetch(url,{
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'X-CSRFToken': csrftoken

                    }
                }); // Response Object

        const responsedata = await response.json();

        return responsedata;


    }

    async put(url,data){

        const response = await fetch(url,{
                    method: 'PUT',
                    body: JSON.stringify(data),
                    headers: {
                    "Content-type": "application/json; charset=UTF-8"
                    }

                }); // Response Object

        const responsedata = await response.json();

        return responsedata;

    }
    async delete(url){


        const response = await fetch(url, {
                method: 'DELETE',
                headers: {
                          "Content-type": "application/json; charset=UTF-8",
                            'X-CSRFToken': csrftoken

                        }
                }); // Response Object

        return await response.json();



    }

}
