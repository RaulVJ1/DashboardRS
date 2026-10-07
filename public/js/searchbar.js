//import { showCityDetails } from './manage_city_data.js';

let data = [];
const MAX_RESULTS = 5;

fetch("data/municipios_rs_filtrados.json")
  .then(response => response.json())
  .then(json => {
    data = json;
  });

const searchInput = document.getElementById("searchInput");
const resultsList = document.getElementById("results");

searchInput.addEventListener("blur", (e) => {
    if (!resultsList.contains(e.relatedTarget)) {
        resultsList.innerHTML = "";
    }
});

resultsList.addEventListener("click", (e) => {
    const item = e.target.closest("li");
    if (!item) return;

    // do something with the selected item
    searchInput.value = item.textContent;
    resultsList.innerHTML = "";
});

searchInput.addEventListener("input", function () {
    const searchTerm = searchInput.value.toLowerCase();

    if (searchTerm === "") {
        resultsList.innerHTML = "";
        return;
    }

    const filteredData = data.filter(item =>
        item.nome.toLowerCase().includes(searchTerm)
    );

    // Limit to MAX_RESULTS using slice
    const limitedResults = filteredData.slice(0, MAX_RESULTS);
    displayResults(limitedResults);
});

function focusCity(city) {
    window.map.setView([city.latitude, city.longitude], 15);
}

function displayResults(items) {
  resultsList.innerHTML = "";

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item.nome;
    li.tabIndex = -1;
    
    // Add click handler
    li.addEventListener("click", function() {
      focusCity(item);
      console.log(item);
    });
    
    // Add some visual feedback that it's clickable
    li.style.cursor = "pointer";
    li.style.padding = "5px";
    
    resultsList.appendChild(li);
  });
}