// const { load } = require("mime");

function addToLocalStorage(key,data){
    localStorage.setItem(key) = data;
}

function retrieveFromLocalStorage(key){
    return localStorage.getItem(key)
}

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
            resdata = JSON.parse(response)
            
            $("#date_legend").empty().append("Date: ")
            $("#date").empty().append(resdata.date)

            $("#calories_legend").empty().append("Calories: ")
            $("#calories").empty().append(resdata.calories)

            $("#burnout_legend").empty().append("Burnout: ")
            $("#burnout").empty().append(resdata.burnout)

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