// careerStatistics.js
const careerStatistics = [
    "300+ AVG Career Batting",
    "200+ Wins Career Pitching",
    "2000+ K Career Pitching",
    "2000+ Hits Career Batting",
    "300+ HR Career Batting",
    "300+ Saves Career Pitching",
    "300+ Wins Career Pitching",
    "3000+ K Career Pitching",
    "3000+ Hits Career Batting",
    "40+ WAR Career (calculated)",
    "≤ 3.00 ERA Career Pitching (calculated)"
];

// Function to create career statistics options dynamically
function createCareerStatsOptions(container, dropdownId) {
    const statsDropdown = document.createElement('select');
    statsDropdown.name = `${dropdownId}_details`;
    statsDropdown.id = `${dropdownId}_details`;
    statsDropdown.required = true;

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    defaultOption.textContent = "Select a Career Statistic";
    statsDropdown.appendChild(defaultOption);

    // Add career statistics options dynamically
    careerStatistics.forEach(stat => {
        const option = document.createElement('option');
        option.value = stat;
        option.textContent = stat;
        statsDropdown.appendChild(option);
    });

    container.appendChild(statsDropdown);
}