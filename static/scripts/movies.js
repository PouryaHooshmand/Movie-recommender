document.addEventListener("DOMContentLoaded", function () {
    const ratingLinks = document.querySelectorAll(".rating-link, .rated-link");

    ratingLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        // Print the id of the clicked element
        var movie_id = link.classList.item(0).substring(1);
        var rating = link.classList.item(1).substring(1);

        fetch("rate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({"movie_id": movie_id, "rating": rating}),
        })
        .then((response) => response.json())
        .then(data => {
          // Handle the response from the server (if needed)
          const movieRatedLinks = document.querySelectorAll(".rated-link.m".concat(movie_id));
          movieRatedLinks.forEach(function(rlink) {
            rlink.classList.add("rating-link");
            rlink.classList.remove("rated-link");
            rlink.removeAttribute("style");
          });
        })
        .catch(error => {
          console.error("Error:", error);
        })
        .finally(() => {
          // Hide the Submit button and show the Edit button
          link.classList.remove("rating-link");
          link.classList.add("rated-link");
          link.style.cssText = `
            pointer-events: none; 
            color: black;
            text-decoration: none;
            font-weight: bold;
          `;
        });




      });
    });
  });
window.onbeforeunload = function () {
  window.scrollTo(0, 0);
}