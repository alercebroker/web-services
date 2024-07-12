let boolDisplay = 1;
let auxBool;
const arrowDown = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                                </svg>`

const arrowUp = `<svg class='tw-h-6 tw-w-6' xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
                        </svg>`

export function howManyGraphsFilter(db){

    const uniqueList = []

    for (let i = 0; i < db.length; i++){ 
        if (!uniqueList.includes(db[i].classifier_name)){
            uniqueList.push(db[i].classifier_name)
        }
    }

    return uniqueList

}

export function hasBodyClass(className) {
   const body = document.body;
    return body.classList.contains(className);
}


// This function detects if there is more than one classifier_name with the same value and detects what of them is the higher version.
export function uniqueValues(tax ,uniqueNameAux) {

    let uniqueName = [];
    let uniqueVersion = [];
    let repeatedArray = []; // if len(repeatedArray[i]) > 1 then there  is a repetition in i

    for (let i = 0; i < tax.length; i++){

        if(!(uniqueName.includes(tax[i].classifier_name))){
            uniqueName.push(tax[i].classifier_name);
            uniqueVersion.push(tax[i].classifier_version)
            repeatedArray.push([tax[i].classifier_version]) 
        } else {
            repeatedArray[uniqueName.indexOf(tax[i].classifier_name)].push(tax[i].classifier_version)
        }

    }

    for (let j = 0; j < repeatedArray.length; j++){

        let maxVersion = 0;

        if (repeatedArray[j].length > 1){
            for (let k = 0; k < repeatedArray[j].length; k++){

                let splitted = repeatedArray[j][k].split('_');
                let splitted_numbers = splitted[splitted.length - 1].split('.')
                let partialSum = 0;

                for (let i = 0;i < splitted_numbers.length; i++){
                    partialSum += Number(splitted_numbers[i]);

                }

                if (maxVersion < partialSum){
                    maxVersion = partialSum;
                    uniqueVersion[j] = repeatedArray[j][k];
                }
            }
        }

    }

    if (uniqueName.length > uniqueNameAux.length){
        uniqueName = uniqueNameAux;
    }

    return [uniqueName,uniqueVersion]

}

// generateDictionaries functions takes the uniqueValues return and generates a dictionary of empty dictionaries, one for every classifier_name in the uniqueValues return
export function generateDictionaries(tax, uniqueNameAux) {

    const [uniqueName,uniqueVersion] = uniqueValues(tax, uniqueNameAux);
    const result = {};

    for (let i = 0; i < uniqueName.length; i++) {
        result[uniqueName[i]] = {};
    }

    return [result,uniqueName,uniqueVersion];
}

// getData is the function that fill the dictionary generated in generateDictionaries. tha data is separated by his classfier_name and added as: class_name:probability
        // where class_name is the key and probability is the value
        // uniqueVersion is not used because db only has 1 version, but if we must choose the higher version, then the uniqueVersion list has it.
export function getData(db, tax, uniqueNameAux){

    const [principalDict,uniqueKeys,uniqueVersion] = generateDictionaries(tax, uniqueNameAux);
    for (let i = 0; i < db.length; i++){
        principalDict[db[i].classifier_name][db[i].class_name] = db[i].probability;
    }

    return [principalDict,uniqueKeys]
}

// selector function returns the dictionary required in the initial moment and when the user selects another chart
export function selector(n, principalDict, uniqueKeys){
    return principalDict[uniqueKeys[n]];
}

export function isDarkMode() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export function getTextColor() {

    const element = document.getElementById('myElement');
    const computedStyle = window.getComputedStyle(element);
    const color = computedStyle.getPropertyValue('color');

    return color 
}

export function handleDarkModeChange(e) {
    var isDarkModeOn = e.matches;
    if (isDarkModeOn){
        myChart.options.r.grid.color = 'white';
    } else {
        myChart.options.r.grid.color = 'black';
    };
};
// Function to capitalize just the first letter of a word
export function capitalize(word){
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}
// Function that split the word by the _ and joins with spaces and capitalized words
export function changeTitles(uniqueKeys){
    let keysTitle = [];

    for (let i = 0; i < uniqueKeys.length; i++){

        let splittedWord = uniqueKeys[i].split('_');
        let auxList = []

        for (let j = 0; j < splittedWord.length; j++){
            auxList.push(capitalize(splittedWord[j]));
        }
        keysTitle.push(auxList.join(' '))
    }
    return keysTitle;
}

export function getComputedColor() {
    const element = document.getElementById('myElement');
    const style = window.getComputedStyle(element);
    return style.color;
}

export function onColorChange(callback) {
    let currentColor = getComputedColor();

    // Check for changes periodically
    setInterval(() => {
        const newColor = getComputedColor();
        if (newColor !== currentColor) {
        currentColor = newColor;
        callback(currentColor);
        }
    }, 100); // Check every 100ms
    }
export function displayMenu(auxBool = 0) {

    const mySelect = document.getElementById('mySelect');
    const arrowSvg = document.getElementById('arrow-svg');
    const robot = document.getElementById('robot');
    const displayButton = document.getElementById('display-button');

    if (auxBool === 1){
        boolDisplay = 0;
    }

    if (boolDisplay === 1) {
        mySelect.style.display = 'block';
        arrowSvg.innerHTML = arrowUp;
        robot.classList.remove('tw-text-black', 'dark:tw-text-white');
        robot.classList.add('tw-text-[#1976d2]');
        arrowSvg.classList.remove('tw-text-black', 'dark:tw-text-white');
        arrowSvg.classList.add('tw-text-[#1976d2]');
        displayButton.classList.remove('tw-border-b-black','dark:tw-border-b-white');
        displayButton.classList.add('tw-border-b-[#1976d2]');
        boolDisplay = 0;
    } else {
        mySelect.style.display = 'none';
        arrowSvg.innerHTML = arrowDown;
        robot.classList.add('tw-text-black', 'dark:tw-text-white');
        robot.classList.remove('tw-text-[#1976d2]');
        arrowSvg.classList.remove('tw-text-[#1976d2]');
        arrowSvg.classList.add('tw-text-black', 'dark:tw-text-white');
        displayButton.classList.remove('tw-border-b-[#1976d2]');
        displayButton.classList.add('tw-border-b-black','dark:tw-border-b-white');
        boolDisplay = 1;
    };
};
