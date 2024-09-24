const headCross = ['Attribute', 'unit', 'value'];

let arrowDown = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                        </svg>`;

let arrowUp = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
            <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
            </svg>`   

export function initCrossmatch(){

    const rawCross = JSON.parse(document.getElementById("crossmatch-data").text);

    // Getting all keys
    const crossKeys = [];
    for (let i = 0; i < Object.values(rawCross).length; i++){

        crossKeys.push(Object.keys(Object.values(rawCross)[i])[0])

    };

    let lengthList = [];
    for (let i = 0; i < crossKeys.length; i++){
        lengthList.push(Object.keys(Object.values(rawCross)[i][crossKeys[i]]).length)
    };

    const n = rawCross.length;
    const tableContainer = document.getElementById('tables-container');
    tableContainer.classList = 'tw-h-full'
    // Initial binaryVector
    var binaryVector = new Array(n).fill(0)

    // This loop creates the text of distance and names for every necesary row. 
    // Also puts a unique id for every div. The two paragraphs are in the same div.
    var idList = [];
    var idButtons = [];
    for (let i = 0; i < n; i++){
        
        // parentDiv is the div that will contain the div with paragraphs and the div with the tables
        var parentDiv = document.createElement('div');
        parentDiv.id = 'parent-'+String(crossKeys[i])
        parentDiv.classList = 'tw-bg-[#1e1e1e] tw-w-[90%] tw-block tw-h-fit tw-ml-[30px] tw-rounded-[4px] tw-text-black dark:tw-text-white tw-border-opacity-10 tw-border-[0px] tw-border-b-[1px] tw-border-b-solid tw-border-b-black dark:tw-border-b-white';
        
        // First paragraph to put the name of the row
        const nameParagraph = document.createElement('p');
        nameParagraph.classList = 'dark:tw-text-white tw-text-black tw-m-[5px] tw-text-left tw-float-left';
        nameParagraph.textContent = crossKeys[i];

        const lenghtParagraph = document.createElement('p');
        lenghtParagraph.classList = 'dark:tw-text-gray-600 tw-text-black tw-m-[5px] tw-text-left tw-float-left';
        lenghtParagraph.textContent = `(` + String(lengthList[i]) + ` attributes)`;

        // We define the arrow in a div to put in the second paragraph                 

        let arrowDiv = document.createElement('div');
        arrowDiv.innerHTML = arrowDown;
        arrowDiv.id = 'arrow' + String(i);
        arrowDiv.classList = 'tw-ml-[5px]'

        // Second paragraph to show the distance and the arrow
        const distanceParagraph = document.createElement('p');
        distanceParagraph.classList = 'tw-flex dark:tw-text-white tw-text-black tw-text-right tw-float-right';

        // Esta es la clave para poder ocultar los botones dependiendo del input. Object.values(rawCross[i][String(crossKeys[i])].distance)[1].toFixed(3) es el value.
        const distanceCross = 'Distance: ' + String(Object.values(rawCross[i][String(crossKeys[i])].distance)[1].toFixed(3)) + '  ' + String(Object.values(rawCross[i][String(crossKeys[i])].distance)[0]);

        // We put the necesary text and appendchild the arrowdiv to the second paragraph
        distanceParagraph.textContent = distanceCross;
        distanceParagraph.appendChild(arrowDiv);

        // newDiv is the div that contains the two paragraphs.
        const newDiv = document.createElement('div');

        newDiv.id = crossKeys[i];
        newDiv.classList = 'tw-overflow-hidden tw-rounded-[4px] tw-w-full tw-h-fit tw-bg-white dark:tw-bg-[#1e1e1e] tw-shadow-2xl tw-text-left tw-mb-[1px] tw-border-[0px] tw-border-white dark:tw-border-[#1e1e1e]';

        newDiv.appendChild(nameParagraph);
        newDiv.appendChild(lenghtParagraph)
        newDiv.appendChild(distanceParagraph);

        // we put newdiv into parentdiv
        parentDiv.appendChild(newDiv);
        parentDiv.classList = 'tw-w-full';

        // we create the div that will contain the table
        const tableDiv = document.createElement('div');
        tableDiv.classList = 'tw-w-full'

        // we create the table and all his childs
        var newTable = document.createElement('table');
        
        idList.push('tb-'+crossKeys[i]);
        newTable.id = 'tb-'+crossKeys[i];
        newTable.classList = 'tw-hidden tw-table dark:tw-text-white tw-w-full tw-shadow-2xl';

        var newThead = document.createElement('thead');
        
        let newTr = document.createElement('tr');
        newTr.classList = 'tw-border-b-[1px] tw-border-b-solid tw-border-b-black dark:tw-border-b-white tw-border-opacity-10 hover:tw-bg-[#757575] tw-mb-[2px] tw-w-full'
        
        // This loop creates the head of the table with the keys of the dictionary
        for (let i = 0; i < headCross.length; i++){

            let newTd1 = document.createElement('td');
            newTd1.classList = 'tw-px-2 tw-py-1 tw-text-left'
            if (i % 3 != headCross.length-1){
                newTd1.setAttribute('style',`width: ${100/3}%`)
            }

            newTd1.innerHTML = headCross[i];

            newTr.appendChild(newTd1);
            newThead.appendChild(newTr);
            newTable.appendChild(newThead);
            Object.keys(rawCross[i][String(crossKeys[i])]).length
        }

        // we put the table into the table div
        tableDiv.appendChild(newTable);

        // we put the table div into the parentdiv
        parentDiv.appendChild(tableDiv);

        var newTbody = document.createElement('tbody');
        newTbody.classList = 'tw-w-full'
        let m = Object.keys(rawCross[i][crossKeys[i]]).length;
        // This loop creates the body of the current selected item. Here, m represents the future length of the rows of every variable. m value can change for 
        // different variable.
        for (let j = 0; j < m; j++){

            let newRow = document.createElement('tr');
            newRow.classList = ' tw-border-[0px] tw-border-b-[1px] tw-border-b-solid tw-border-b-black dark:tw-border-b-white tw-border-opacity-10 hover:tw-bg-[#757575] tw-mb-[2px] tw-w-full'

            for (let k = 0; k < headCross.length; k++){

                let newTd2 = document.createElement('td');
                newTd2.classList = 'tw-px-2 tw-py-1 tw-text-left'
                //if (k % 3 != headCross.length-1){
                //    newTd2.setAttribute('style',`width: ${100/3}%`)
                //}
                if (k === 0){
                    newTd2.innerHTML = Object.keys(rawCross[i][crossKeys[i]])[j];
                } else if (k === 1) { 
                    newTd2.innerHTML = Object.values(rawCross[i][crossKeys[i]])[j].unit;
                } else {
                    newTd2.innerHTML = Object.values(rawCross[i][crossKeys[i]])[j].value;
                };

                newRow.appendChild(newTd2);
                newTbody.appendChild(newRow);
                newTable.appendChild(newTbody);
            }

            tableDiv.appendChild(newTable);
            parentDiv.appendChild(tableDiv);
        
        }      

        // we create  the button  that will contain the parentdiv.
        const newButton = document.createElement('button');
        idButtons.push('button' + String(i));
        newButton.id = 'button' + String(i); // aque hay que poner la distancia 
        newButton.value = String(Object.values(rawCross[i][String(crossKeys[i])].distance)[1].toFixed(3));
        newButton.addEventListener('click', () => {
            binaryVectorUpdate('tb-'+String(crossKeys[i]), idList, binaryVector)
            changeArrow('arrow' + String(i));
        })
        newButton.classList = 'tw-bg-[#1e1e1e] tw-w-[90%] tw-ml-[30px] tw-min-h-[64px] tw-rounded-[4px] tw-text-black dark:tw-text-white tw-border-opacity-10 tw-border-[0px] tw-border-b-[1px] tw-border-b-solid tw-border-b-black dark:tw-border-b-white'

        // we put the parent div into the newbutton. this makes that all the row works like a button.
        newButton.appendChild(parentDiv)

        // we put the entire button-row into the table container
        tableContainer.appendChild(newButton);
    }

    // control of input and slider 

    const slider = document.getElementById('slider');
    const numberInput = document.getElementById('numberInput');


    const customInput = document.getElementById('customInput');

    customInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
        }
    });

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

        slider.value = filteredValue;
        hideButtonWithTables(filteredValue, idButtons);
    });

    slider.addEventListener('input', function() {
        //customInput.value = this.value;
        customInput.innerHTML = this.value;
        hideButtonWithTables(this.value, idButtons);
});


}


let boolArrow = 1;
function changeArrow(arrow){

    if (boolArrow === 0){
        document.getElementById(arrow).innerHTML = arrowDown;
        boolArrow = 1;
    } else {
        document.getElementById(arrow).innerHTML = arrowUp;
        boolArrow = 0;
    }
}
// this function closes a table if the user click twice in the same row (open-close) and if the user clicks in another, closes the current table.
function binaryVectorUpdate(id, idList, binaryVector){
    
    const pos = idList.indexOf(id);
    if (pos === binaryVector.indexOf(1)){

        document.getElementById(idList[pos]).style.display = 'none'

        binaryVector[pos] = 0

    } else {

        for (let i = 0; i < binaryVector.length; i++){
            
            if (binaryVector[i] === 1){

                document.getElementById(idList[i]).style.display = 'none'

                binaryVector[i] = 0;

            };

        };
        // we put a 1 in the current row clicked
        binaryVector[pos] = 1;
        displayCrossmatch(binaryVector, idList);

    }


};  
// this function shows the current table selected by the user
function displayCrossmatch(binaryVector, idList){

    const pos = binaryVector.indexOf(1);   

    document.getElementById(String(idList[pos])).style.display = 'table'

};

// function to hide buttons/tables if the distance is below the required

function hideButtonWithTables(val, idButtons){   
    for (let i = 0; i < idButtons.length; i++){
        if (parseFloat(document.getElementById(idButtons[i]).value) >= val){
            document.getElementById(idButtons[i]).style.display = 'none'; 
        } else {
            document.getElementById(idButtons[i]).style.display = 'block'; 
        }
    }
}

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


