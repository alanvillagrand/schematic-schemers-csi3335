// Generate an array of years from 1871 to 2022
const years = Array.from({ length: 2022 - 1871 + 1 }, (_, i) => 2022 - i);

// Function to populate a dropdown with years
function populateYearsDropdown() {
    const dropdown = document.getElementById("yearsDropdown");
    years.forEach((year) => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        dropdown.appendChild(option);
    });
}

// Run the function once the page loads
document.addEventListener("DOMContentLoaded", populateYearsDropdown);
