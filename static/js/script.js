// const { load } = require("mime");
// it been use in the layout.html file, the funtion are self explainning


function addToLocalStorage(key,data){
    localStorage.setItem(key) = data;
}

function retrieveFromLocalStorage(key){
    return localStorage.getItem(key)
}

/**
 * Sends a POST request to log out the user and redirects to the login page upon success.
 */
function logout(){
    $.ajax({
        type: "POST",
        url: "/logout",
        success: function(data) {
            console.log(data)
            window.location.href = "login";
        }
    });
}

/**
 * Handles the history form the calories page and updates history data
 *  with the new food or burn out.
 * @param {Event} e - The form submission event.
 */
function history(e){
    const form = new FormData(e.target);
    date = form.get("date")
    console.log(date)
    $.ajax({
        type: "POST",
        url: "/ajaxhistory",
        data:{
            "date":date
        },
        success: function(response){
            console.log(response)
            // let resdata = JSON.parse(response)
            // console.log(resdata)
            
            $("#date_legend").empty().append("Date: ")
            $("#date").empty().append(response["date"])

            $("#foods_legend").empty().append("Foods Log: ")
            $("#foods").empty().append(response["foods"])

            $("#calories_legend").empty().append("Total Calories Gained: ")
            $("#calories").empty().append(response["cals_in"])

            $("#activities_legend").empty().append("Activities Log: ")
            $("#activities").empty().append(response["activities"])

            $("#burnout_legend").empty().append("Total Calories Burned: ")
            $("#burnout").empty().append(response["cals_out"])

            $("#net_legend").empty().append("Net Total Calories: ")
            $("#net").empty().append(response["net"])

            $("#history-data").empty().append(JSON.stringify(response));
        }
    })
}

function sendRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxsendrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function cancelRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxcancelrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function approveRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxapproverequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function dashboard(e, email){
    $.ajax({
        type: "POST",
        url: "/ajaxdashboard",
        data:{
            "email":email
        },
        success: function(response){
            console.log(response)
            resdata = JSON.parse(response)
            
            $("#enroll_legend").empty().append("ENrolled: ")
            $("#enroll").empty().append(resdata.enroll)
        }
    })
}