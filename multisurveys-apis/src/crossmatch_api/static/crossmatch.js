
let currentOpenTable = null; 

let arrowDown = `<svg class='tw-h-5 tw-w-5' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                        </svg>`;

let arrowUp = `<svg class='tw-h-5 tw-w-5' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
            </svg>`   

export function initCrossmatch() {
    // Getting data
    let crossKeys = JSON.parse(document.getElementById("crossmatch-data-keys").text);
    // Adding event listeners to the buttons to show or hide the tables
    for (let j = 0; j < crossKeys.length; j++){
        let button = document.getElementById(crossKeys[j])
        if (button){

            button.addEventListener('click', function() {
                showTable(crossKeys[j]);
            });
            
            document.getElementById(`arrows-${crossKeys[j]}`).innerHTML = arrowDown;
        }
    };

    let customInput = document.getElementById('customInput');
    let slider = document.getElementById('slider');

    customInput.innerHTML = customInput.getAttribute('value');

    // Event listener of the slider
    slider.addEventListener('input', function() {
        customInput.innerHTML = this.value;
        inspectButtons(this.value, crossKeys);
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
        inspectButtons(filteredValue, crossKeys);
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

function showTable(key) {
    let table = document.getElementById(`table-${key}`);
    let arrow = document.getElementById(`arrows-${key}`);
    if (table){

        if (currentOpenTable && currentOpenTable !== table) {
            // Close the currently open table
            currentOpenTable.classList.add('tw-hidden');
            currentOpenTable.classList.remove('tw-table');
            let currentOpenArrow = document.getElementById(`arrows-${currentOpenTable.id.replace('table-', '')}`);
            currentOpenArrow.innerHTML = arrowDown;
        }
        
        if (table.classList.contains('tw-hidden') || !table.classList.contains('tw-table')) {
            // Open the clicked table
            table.classList.remove('tw-hidden');
            table.classList.add('tw-table');
            arrow.innerHTML = arrowUp;
            currentOpenTable = table;
        } else {
            // Close the clicked table if it's already open
            table.classList.add('tw-hidden');
            table.classList.remove('tw-table');
            arrow.innerHTML = arrowDown;
            currentOpenTable = null;
        }
    }
}

// Function to visit every button and call the hideButtons function
function inspectButtons(sliderValue, crossKeys){
    for (let i = 0; i < crossKeys.length; i++) {
        let element = document.getElementById(crossKeys[i]);
        if (element) {
            let arcsecDistance = element.getAttribute('arcsec-dist');
            let key = element.getAttribute('data-key');
            hideButtons(arcsecDistance, key, sliderValue);
        };
    };
};

// this functions will hide the button if the slider value is lower than the object arcsed distance associated to the button
function hideButtons(arcsecDistance, key, sliderValue) {
    let button = document.getElementById(`row-${key}`);

    if (parseFloat(arcsecDistance) >= parseFloat(sliderValue)) {
        button.classList.add('tw-hidden');
        button.classList.remove('tw-table-row');
    } else {
        button.classList.remove('tw-hidden');
        button.classList.add('tw-table-row');
    }
}