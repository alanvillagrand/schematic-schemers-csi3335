// teams.js
/*
const teams = [
    "Altoona Mountain City",
    "Anaheim Angels",
    "Arizona Diamondbacks",
    "Atlanta Braves",
    "Baltimore Canaries",
    "Baltimore Marylands",
    "Baltimore Monumentals",
    "Baltimore Orioles",
    "Baltimore Terrapins",
    "Boston Americans",
    "Boston Beaneaters",
    "Boston Bees",
    "Boston Braves",
    "Boston Doves",
    "Boston Red Caps",
    "Boston Red Sox",
    "Boston Red Stockings",
    "Boston Reds",
    "Boston Rustlers",
    "Brooklyn Atlantics",
    "Brooklyn Bridegrooms",
    "Brooklyn Dodgers",
    "Brooklyn Eckfords",
    "Brooklyn Gladiators",
    "Brooklyn Grays",
    "Brooklyn Grooms",
    "Brooklyn Robins",
    "Brooklyn Superbas",
    "Brooklyn Tip-Tops",
    "Brooklyn Ward's Wonders",
    "Buffalo Bisons",
    "Buffalo Blues",
    "Buffalo Buffeds",
    "California Angels",
    "Chicago Chi-Feds",
    "Chicago Colts",
    "Chicago Cubs",
    "Chicago Orphans",
    "Chicago Pirates",
    "Chicago Whales",
    "Chicago White Sox",
    "Chicago White Stockings",
    "Chicago/Pittsburgh (Union League)",
    "Cincinnati Kelly's Killers",
    "Cincinnati Outlaw Reds",
    "Cincinnati Red Stockings",
    "Cincinnati Redlegs",
    "Cincinnati Reds",
    "Cleveland Blues",
    "Cleveland Bronchos",
    "Cleveland Forest Citys",
    "Cleveland Guardians",
    "Cleveland Indians",
    "Cleveland Infants",
    "Cleveland Naps",
    "Cleveland Spiders",
    "Colorado Rockies",
    "Columbus Buckeyes",
    "Columbus Solons",
    "Detroit Tigers",
    "Detroit Wolverines",
    "Elizabeth Resolutes",
    "Florida Marlins",
    "Fort Wayne Kekiongas",
    "Hartford Dark Blues",
    "Houston Astros",
    "Houston Colt .45's",
    "Indianapolis Blues",
    "Indianapolis Hoosiers",
    "Kansas City Athletics",
    "Kansas City Cowboys",
    "Kansas City Packers",
    "Kansas City Royals",
    "Keokuk Westerns",
    "Los Angeles Angels",
    "Los Angeles Angels of Anaheim",
    "Los Angeles Dodgers",
    "Louisville Colonels",
    "Louisville Eclipse",
    "Louisville Grays",
    "Miami Marlins",
    "Middletown Mansfields",
    "Milwaukee Braves",
    "Milwaukee Brewers",
    "Milwaukee Grays",
    "Minnesota Twins",
    "Montreal Expos",
    "New Haven Elm Citys",
    "New York Giants",
    "New York Gothams",
    "New York Highlanders",
    "New York Metropolitans",
    "New York Mets",
    "New York Mutuals",
    "New York Yankees",
    "Newark Pepper",
    "Oakland Athletics",
    "Philadelphia Athletics",
    "Philadelphia Blue Jays",
    "Philadelphia Centennials",
    "Philadelphia Keystones",
    "Philadelphia Phillies",
    "Philadelphia Quakers",
    "Philadelphia Whites",
    "Pittsburg Alleghenys",
    "Pittsburgh Burghers",
    "Pittsburgh Pirates",
    "Pittsburgh Rebels",
    "Providence Grays",
    "Richmond Virginians",
    "Rochester Broncos",
    "Rockford Forest Citys",
    "San Diego Padres",
    "San Francisco Giants",
    "Seattle Mariners",
    "Seattle Pilots",
    "St. Louis Brown Stockings",
    "St. Louis Browns",
    "St. Louis Cardinals",
    "St. Louis Maroons",
    "St. Louis Perfectos",
    "St. Louis Red Stockings",
    "St. Louis Terriers",
    "St. Paul White Caps",
    "Syracuse Stars",
    "Tampa Bay Devil Rays",
    "Tampa Bay Rays",
    "Texas Rangers",
    "Toledo Blue Stockings",
    "Toledo Maumees",
    "Toronto Blue Jays",
    "Troy Haymakers",
    "Troy Trojans",
    "Washington Blue Legs",
    "Washington Nationals",
    "Washington Olympics",
    "Washington Senators",
    "Washington Statesmen",
    "Wilmington Quicksteps",
    "Worcester Ruby Legs"
];
*/

const teams = [
    'Only One Team',
    'Arizona Diamondbacks',
    'Atlanta Braves',
    'Baltimore Orioles',
    'Boston Red Sox',
    'Chicago Cubs',
    'Chicago White Sox',
    'Cincinnati Reds',
    'Cleveland Guardians',
    'Colorado Rockies',
    'Detroit Tigers',
    'Houston Astros',
    'Kansas City Royals',
    'Los Angeles Angels',
    'Los Angeles Dodgers',
    'Miami Marlins',
    'Milwaukee Brewers',
    'Minnesota Twins',
    'New York Mets',
    'New York Yankees',
    'Oakland Athletics',
    'Philadelphia Phillies',
    'Pittsburgh Pirates',
    'San Diego Padres',
    'San Francisco Giants',
    'Seattle Mariners',
    'St. Louis Cardinals',
    'Tampa Bay Rays',
    'Texas Rangers',
    'Toronto Blue Jays',
    'Washington Nationals',
]

function populateTeamsDropdown() {
    const dropdown = document.getElementById("teamsDropdown");
    teams.forEach((team) => {
        const option = document.createElement("option");
        option.value = team;
        option.textContent = team;
        dropdown.appendChild(option);
    });
}

document.addEventListener("DOMContentLoaded", populateTeamsDropdown);