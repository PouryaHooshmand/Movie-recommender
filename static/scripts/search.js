function search() {
    const searchContainer = document.getElementById('search-container');

    // Get the search input value
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();
    // Redirect to the search results page with the search and website terms as parameters
    window.location.href = 'search?q=' + encodeURIComponent(searchTerm);
}


function enableButton() {
    if(document.getElementById("search-input").value==="") { 
           document.getElementById('search-button').disabled = true; 
       } else { 
           document.getElementById('search-button').disabled = false;
       }
}

