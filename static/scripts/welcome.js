document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById("submitButton");
    const favsCheckBox = document.getElementsByClassName("favsCheckBox");
    const favsEditMessage = document.getElementById("favsEditMessage");
    const firstName = document.getElementById("fname-input");
    const lastName = document.getElementById("lname-input");

  

    
    submitButton.addEventListener("click", function () {

        var newFavs = {"first_name": firstName.value, "last_name": lastName.value};
        // Disable input fields
        for (var i = 0; i < favsCheckBox.length; i++) {
            if (favsCheckBox[i].checked) {
                newFavs[favsCheckBox[i].id]=true;
              } else {
                newFavs[favsCheckBox[i].id]=false;
              }
        }
      
        fetch("set_user_profile", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newFavs),
      })
      .then((response) => response.json())
      .then(data => {
        // Handle the response from the server (if needed)
        favsEditMessage.textContent = data["message"];
        favsEditMessage.disabled = false;
      })
      .catch(error => {
        console.error("Error:", error);
      })
      .finally(() => {
        window.location.replace("/");
      });
      
      });
  });
  
function enableButton() {
    if(document.getElementById("fname-input").value==="" || document.getElementById("lname-input").value==="") { 
           document.getElementById('submitButton').disabled = true; 
       } else { 
           document.getElementById('submitButton').disabled = false;
       }
}