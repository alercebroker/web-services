
var crossKeysRaw = [];
var crossKeys = [];

export function initCrossmatch() {
    // Getting data
    const rawCross = JSON.parse(document.getElementById("crossmatch-data").text);
    // Get all keys of the dict
    crossKeysRaw = [];
    for (let i = 0; i < Object.values(rawCross).length; i++){
        crossKeysRaw.push(Object.keys(Object.values(rawCross)[i])[0])
    };
    // Filter all the objects with distance more than 20 arcsed
    crossKeys = [];
    for (let i = 0; i < crossKeysRaw.length; i++){
        if (rawCross[i][crossKeysRaw[i]]['distance']['value'] <= 20){
            crossKeys.push(crossKeysRaw[i])
        }
    };
    // Adding event listeners to the buttons to show or hide the tables
    for (let j = 0; j < crossKeys.length; j++){
        console.log(crossKeys[j])
        document.getElementById(crossKeys[j]).addEventListener('click', function() {
            showTable(crossKeys[j]);
        });
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
// This part prevents to the function being called multiple times, just every 0.2s 
const throttledShowTable = throttle(function(key) {
    const table = document.getElementById(`table-${key}`);
    if (table) {
        table.style.display = table.style.display === 'block' ? 'none' : 'block';
    }
}, 200);

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

    const button = document.getElementById(`${key}`);
    if (parseFloat(arcsecDistance) >= parseFloat(sliderValue)){
        button.style.display = 'none'; 
    } else {
        button.style.display = 'block'; 
    };

};