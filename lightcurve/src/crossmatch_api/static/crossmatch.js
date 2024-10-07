
var crossKeysRaw = [];
var crossKeys = [];
var currentOpenTable = null; 

let arrowDown = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                        </svg>`;

let arrowUp = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
            </svg>`   

export function initCrossmatch() {
    // Getting data
    const rawCross = JSON.parse(document.getElementById("crossmatch-data").text);
    // Get all keys of the dict
    crossKeysRaw = [];
    for (let i = 0; i < Object.values(rawCross).length; i++){
        crossKeysRaw.push(Object.keys(Object.values(rawCross)[i])[0])
    };
    // Filter all the objects with distance more than 20 arcsec
    crossKeys = [];
    for (let i = 0; i < crossKeysRaw.length; i++){
        if (rawCross[i][crossKeysRaw[i]]['distance']['value'] <= 20){
            crossKeys.push(crossKeysRaw[i])
        }
    };
    // Adding event listeners to the buttons to show or hide the tables
    for (let j = 0; j < crossKeys.length; j++){
        document.getElementById(crossKeys[j]).addEventListener('click', function() {
            showTable(crossKeys[j]);
        });

        document.getElementById(`arrows-${crossKeys[j]}`).innerHTML = arrowDown;
    };

    const customInput = document.getElementById('customInput');
    const slider = document.getElementById('slider');

    // Event listener of the slider
    slider.addEventListener('input', function() {
        customInput.innerHTML = this.value;
        inspectButtons(this.value);
    });

    // Prevent line breaks on the input
    customInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            return false; 
        }
    });
    // Event listener of the input where only is allowed to put float number between 0-20
    customInput.addEventListener('input', function() {
        // Remove any line breaks
        this.textContent = this.textContent.replace(/\n/g, '');

        // Remove any characters that are not numbers or dots
        let filteredValue = this.textContent.replace(/[^0-9.]/g, '');
        
        // Ensure only one dot is present
        let parts = filteredValue.split('.');
        if (parts.length > 2) {
            filteredValue = parts[0] + '.' + parts.slice(1).join('');
        }
        // Update the content if it has changed
        if (this.textContent !== filteredValue) {
            this.textContent = filteredValue;
            
            // Move cursor to the end
            let range = document.createRange();
            let sel = window.getSelection();
            range.setStart(this.childNodes[0] || this, this.textContent.length);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
        }
        
        if (filteredValue > 20){
            filteredValue = 20;
            this.textContent = 20;
        }

        slider.value = filteredValue;
        inspectButtons(filteredValue);
    });

};


export function elementReady(selector) {
    return new Promise((resolve, reject) => {
    const el = document.querySelector(selector);
    if (el) {
        resolve(el);
    }

    new MutationObserver((mutationRecords, observer) => {
        Array.from(document.querySelectorAll(selector)).forEach(element => {
        resolve(element);
        observer.disconnect();
        });
    })
    .observe(document.documentElement, {
        childList: true,
        subtree: true
    });
    });
}

//throttleTimer is a variable that calls a functions to prevent multiple calls to the functions
let throttleTimer;

function throttle(func, delay) {
    return function() {
        if (throttleTimer) return;
        const context = this;
        const args = arguments;
        func.apply(context, args);
        throttleTimer = setTimeout(() => {
            throttleTimer = null;
        }, delay);
    };
}
// This part prevents to the function being called multiple times, just every 0.05s 
const throttledShowTable = throttle(function(key) {
    const table = document.getElementById(`table-${key}`);
    const arrow = document.getElementById(`arrows-${key}`);
    if (currentOpenTable && currentOpenTable !== table) {
        // Close the currently open table
        currentOpenTable.style.display = 'none';
        const currentOpenArrow = document.getElementById(`arrows-${currentOpenTable.id.replace('table-', '')}`);
        currentOpenArrow.innerHTML = arrowDown;
    }

    if (table.style.display === 'none' || table.style.display === '') {
        // Open the clicked table
        table.style.display = 'table';
        arrow.innerHTML = arrowUp;
        currentOpenTable = table;
    } else {
        // Close the clicked table if it's already open
        table.style.display = 'none';
        arrow.innerHTML = arrowDown;
        currentOpenTable = null;
    }
}, 50);

function showTable(key) {
    throttledShowTable(key);
}

// Function to visit every button and call the hideButtons function
function inspectButtons(sliderValue){
    for (let i = 0; i < crossKeys.length; i++) {
        const element = document.getElementById(crossKeys[i]);
        if (element) {
            const arcsecDistance = element.getAttribute('arcsec-dist');
            const key = element.getAttribute('data-key');
            hideButtons(arcsecDistance, key, sliderValue);
        };
    };
};

// this functions will hide the button if the slider value is lower than the object arcsed distance associated to the button
function hideButtons(arcsecDistance, key, sliderValue){

    const button = document.getElementById(`row-${key}`);
    if (parseFloat(arcsecDistance) >= parseFloat(sliderValue)){
        button.style.display = 'none'; 
    } else {
        button.style.display = 'table-row'; 
    };

};