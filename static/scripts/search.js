function search() {
    const searchContainer = document.getElementById('search-container');

    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();
    window.location.href = 'search?q=' + encodeURIComponent(searchTerm);
}


function enableButton() {
    if(document.getElementById("search-input").value==="") { 
           document.getElementById('search-button').disabled = true; 
       } else { 
           document.getElementById('search-button').disabled = false;
       }
}

