document.addEventListener("DOMContentLoaded", function () {
    const favsEditButton = document.getElementById("favsEditButton");
    const favsSubmitButton = document.getElementById("favsSubmitButton");
    const favsCheckBox = document.getElementsByClassName("favsCheckBox");
    const favsEditMessage = document.getElementById("favsEditMessage");
  


    favsEditButton.addEventListener("click", function () {
        // Enable input fields
        for (var i = 0; i < favsCheckBox.length; i++) {
            favsCheckBox[i].disabled = false;
        }
        // Show the Submit button and hide the Edit button
        favsSubmitButton.style.display = "inline-block";
        favsEditButton.style.display = "none";
      });
    
      favsSubmitButton.addEventListener("click", function () {

        var newFavs = {};
        // Disable input fields
        for (var i = 0; i < favsCheckBox.length; i++) {
            favsCheckBox[i].disabled = true;
            if (favsCheckBox[i].checked) {
                newFavs[favsCheckBox[i].id]=true;
              } else {
                newFavs[favsCheckBox[i].id]=false;
              }
        }
      
        fetch("update_favs", {
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
        // Hide the Submit button and show the Edit button
        favsSubmitButton.style.display = "none";
        favsEditButton.style.display = "inline-block";
      });
  
      });
  });
  