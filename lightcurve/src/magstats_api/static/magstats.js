const bandMapping = {
  2: "r",
  3: "i",
  1: "g",
};
let currentPage = 1;

const rawDb = JSON.parse(document.getElementById("magstats-data").text);
const db = [];
parseStatR(rawDb);

function parseStatR(dict) {
  Object.keys(dict).forEach((key) => {
    let auxJson = {};
    auxJson = {
      stellar: dict[key]["stellar"],
      corrected: dict[key]["corrected"],
      ndet: dict[key]["ndet"],
      ndubious: dict[key]["ndubious"],
      magmean: dict[key]["magmean"],
      magmax: dict[key]["magmax"],
      magmin: dict[key]["magmin"],
      magsigma: dict[key]["magsigma"],
      maglast: dict[key]["maglast"],
      magfirst: dict[key]["magfirst"],
      firstmjd: dict[key]["firstmjd"],
      lastmjd: dict[key]["lastmjd"],
      step_id_corr: dict[key]["step_id_corr"],
      fid: dict[key]["fid"],
    };
    db.push(auxJson);
  });
}

let numBands = [];

for (let i = 0; i < db.length; i++) {
  numBands.push(db[i]["fid"]);
  delete db[i]["fid"];
}

let realBands = [];

for (let i = 0; i < numBands.length; i++) {
  realBands.push(bandMapping[numBands[i]]);
}

const numColumns = db.length + 1; // Esto  es numero de bandas + 1
const numRows = Object.keys(db[0]).length;

// function hasBodyClass(className) { const body = document.body;
//   return body.classList.contains(className);
// }
// const isDarkMode = hasBodyClass("tw-dark");

////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Here is created the table dinamicly.

// This function creates the entire html structure dinamicly.
function createTable() {
  let columNames = ["Stat"].concat(realBands);

  const tableContainer = document.getElementById("tableContainer");

  // Clear any existing table
  tableContainer.innerHTML = "";

  // Create the table element
  const table = document.createElement("table");
  table.classList =
    "tw-overflow-auto tw-w-full tw-text-sm";

  //const colGroup = document.createElement('colgroup');
  //colGroup.classList = 'tw-w-[95%] tw-mx-auto';

  // Create the table header row
  const headerRow = document.createElement("tr");
  headerRow.classList =
    "hover:tw-opacity-70 hover:tw-cursor-pointer dark:tw-text-white tw-text-black tw-w-full";

  for (let i = 0; i < numColumns; i++) {
    const th = document.createElement("th");
    th.textContent = columNames[i];

    const arrowButton = document.createElement("button");
    arrowButton.setAttribute("id", "arrowButton");

    th.appendChild(arrowButton);
    headerRow.appendChild(th);
  }
  table.appendChild(headerRow);

  const tBody = document.createElement("tbody");
  tBody.setAttribute("id", "dataTableBody");
  // Create the table data rows
  for (let i = 0; i < numRows; i++) {
    const dataRow = document.createElement("tr");
    dataRow.classList =
      "tw-w-full tw-preflight hover:tw-bg-[#757575] dark:tw-text-white tw-text-black tw-border-b-[1px] tw-border-b-solid tw-border-b-black dark:tw-border-b-white tw-border-opacity-20 dark:tw-border-opacity-20";

    for (let j = 0; j < numColumns; j++) {
      const td = document.createElement("td");
      if (j < numColumns - 1) {
        td.setAttribute("style", `max-width: ${(1 / (numColumns - 1)) * 100}%`);
      }
      td.id = `cell-${i}-${j}`;
      dataRow.appendChild(td);
    }
    tBody.appendChild(dataRow);
  }
  //table.appendChild(colGroup)
  table.appendChild(tBody);

  // Append the table to the container
  tableContainer.appendChild(table);
}

// This function inject the data into the html table created in createTable function
function displayColumns() {
  if (boolColumns === 0) {
    for (let j = 0; j < numRows; j++) {
      let name = "cell-" + String(j) + "-" + String(0);
      document.getElementById(name).innerHTML = Object.keys(db[0])[j];
    }
    // Let's note that here i is for columns and j is for rows
    for (let i = 1; i < numColumns; i++) {
      for (let j = 0; j < numRows; j++) {
        let name = "cell-" + String(j) + "-" + String(i);
        document.getElementById(name).innerHTML = Object.values(db[i - 1])[j];
      }
    }

    boolColumns = 1;
  } else {
    for (let j = 0; j < numRows; j++) {
      let name = "cell-" + String(j) + "-" + String(0);
      document.getElementById(name).innerHTML = Object.keys(db[0])[
        numRows - j - 1
      ];
    }
    for (let i = 1; i < numColumns; i++) {
      for (let j = 0; j < numRows; j++) {
        let name = "cell-" + String(j) + "-" + String(i);
        document.getElementById(name).innerHTML = Object.values(db[i - 1])[
          numRows - j - 1
        ];
      }
    }
    boolColumns = 0;
  }
}

// We call the function to create the html structure
createTable();

let boolColumns = 0;
// We call the function to inject the data.
displayColumns();

//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////

// From here the code is only for the display of the rows per page, the buttons and the display menu to select that

// We define the arrows to change the order of the rows display in the  table
const arrowUp = `<svg class="tw-h-5 tw-w-6" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                                    <path stroke="none" d="M0 0h24v24H0z" />
                                    <line x1="12" y1="5" x2="12" y2="19" />
                                    <line x1="16" y1="9" x2="12" y2="5" />
                                    <line x1="8" y1="9" x2="12" y2="5" />
                                </svg>`;

const arrowDown = `<svg class="tw-h-6 tw-w-6"  width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">  <path stroke="none" d="M0 0h24v24H0z" />  <line x1="12" y1="5" x2="12" y2="19" />  <line x1="16" y1="15" x2="12" y2="19" />  <line x1="8" y1="15" x2="12" y2="19" /></svg>`;

document.getElementById("arrowButton").innerHTML = arrowUp;

// We add an event listener to detect if the user wants to change the order
document.getElementById("arrowButton").addEventListener("click", () => {
  displayColumns();

  if (boolColumns === 1) {
    document.getElementById("arrowButton").innerHTML = arrowUp;
  } else {
    document.getElementById("arrowButton").innerHTML = arrowDown;
  }
});

const dataTableBody = document.getElementById("dataTableBody");
const rowSelect = document.getElementById("rowSelect");

// This function change the page of the table if there is less rows selected by the user to show
function navigateTable(direction) {
  let rowsPerPage = parseInt(rowSelect.value);

  currentPage += direction;
  const totalPages = Math.ceil(dataTableBody.rows.length / rowsPerPage);

  if (currentPage < 1) {
    currentPage = 1;
  } else if (currentPage > totalPages) {
    currentPage = totalPages;
  }

  displayRows();
}

// This function decide what rows are showed depends of the rows per page selected by the user
function displayRows() {
  const startIndex = (currentPage - 1) * rowsToShow;
  const endIndex = startIndex + rowsToShow;
  const totalRows = dataTableBody.rows.length;

  const leftArrow = document.getElementById("leftArrow");
  const rightArrow = document.getElementById("rightArrow");
  const firstNumber = document.getElementById("first-number");
  const secondNumber = document.getElementById("second-number");

  // Update numbers
  firstNumber.textContent = startIndex === 0 ? 1 : startIndex + 1;
  secondNumber.textContent = Math.min(endIndex, totalRows);

  // Update arrow colors
  updateArrowColor(leftArrow, startIndex === 0);
  updateArrowColor(rightArrow, endIndex >= totalRows);

  // Show/hide rows
  Array.from(dataTableBody.rows).forEach((row, index) => {
    row.style.display =
      index >= startIndex && index < endIndex ? "table-row" : "none";
  });
}

function updateArrowColor(arrowElement, isDisabled) {
  arrowElement.classList.remove(
    "tw-text-gray-400",
    "tw-text-black",
    "tw-text-white",
    "dark:tw-text-white",
  );
  if (isDisabled) {
    arrowElement.classList.add("tw-text-gray-400");
  } else {
    arrowElement.classList.add("tw-text-black", "dark:tw-text-white");
  }
}

let rowsToShow = 5;
displayRows();

document.getElementById("total-number").innerHTML = dataTableBody.rows.length;
rowSelect.addEventListener("change", () => {
  rowsToShow = parseInt(rowSelect.value);
  currentPage = 1;
  displayRows();
});

const btnLeft = document.getElementById("leftArrow");
const btnRight = document.getElementById("rightArrow");

btnLeft.addEventListener("click", () => {
  navigateTable(-1);
});
btnRight.addEventListener("click", () => {
  navigateTable(1);
});
