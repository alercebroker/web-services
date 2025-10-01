export function initMagstats() {
  let stat_r_keys = JSON.parse(document.getElementById('magstats-data-keys').text);
  let totalRows = stat_r_keys.length;

  updateTable(0, 5, stat_r_keys);
  showNumberOfPages(totalRows);
  arrowsControl(totalRows, stat_r_keys);

  document.getElementById('rowSelect').addEventListener('input', function(){

    // Reiniciar a la primera página cuando se cambia el número de filas
    updateTable(0, parseInt(this.value), stat_r_keys);
    document.getElementById('first-number').textContent = 1;
    document.getElementById('second-number').textContent = Math.min(parseInt(this.value), totalRows);
    arrowsControl(totalRows, stat_r_keys);
  });
};

function updateTable(startIndex, endIndex, stat_r_keys){
  for (let i = 0; i < stat_r_keys.length; i++){
    let key = stat_r_keys[i];
    let currentRow = document.getElementById(`row-${key}`);

    if (i >= startIndex && i < endIndex) {
      currentRow.classList.remove('tw-hidden');
      currentRow.classList.add('tw-table-row');
    } else {
      currentRow.classList.add('tw-hidden');
      currentRow.classList.remove('tw-table-row');
    }
  }
}

function showNumberOfPages(totalRows){
  let rowSelect = document.getElementById('rowSelect');
  let rowsPerPage = parseInt(rowSelect.value);
  
  let firstNumber = 1;
  let secondNumber = Math.min(rowsPerPage, totalRows);
  
  document.getElementById('first-number').textContent = firstNumber;
  document.getElementById('second-number').textContent = secondNumber;
  document.getElementById('total-number').textContent = totalRows;
}

export function arrowsControl(totalRows, stat_r_keys){
  let numberDisplayed = parseInt(document.getElementById('rowSelect').value);
  let currentFirstNumber = parseInt(document.getElementById('first-number').textContent);
  let currentSecondNumber = parseInt(document.getElementById('second-number').textContent);
  let leftArrow = document.getElementById('leftArrow');
  let rightArrow = document.getElementById('rightArrow');
  
  // Deshabilitar flecha izquierda si estamos en la primera página
  if (currentFirstNumber === 1) {
    leftArrow.disabled = true;
    leftArrow.style.opacity = '0.5';
    leftArrow.style.cursor = 'not-allowed';
  } else {
    leftArrow.disabled = false;
    leftArrow.style.opacity = '1';
    leftArrow.style.cursor = 'pointer';
  }
  
  // Deshabilitar flecha derecha si estamos en la última página
  if (currentSecondNumber >= totalRows) {
    rightArrow.disabled = true;
    rightArrow.style.opacity = '0.5';
    rightArrow.style.cursor = 'not-allowed';
  } else {
    rightArrow.disabled = false;
    rightArrow.style.opacity = '1';
    rightArrow.style.cursor = 'pointer';
  }
  
  // Event listener para flecha izquierda
  leftArrow.onclick = function() {
    if (currentFirstNumber > 1) {
      let newFirst = Math.max(1, currentFirstNumber - numberDisplayed);
      let newSecond = Math.min(newFirst + numberDisplayed - 1, totalRows);
      
      let startIndex = newFirst - 1;
      let endIndex = newSecond;
      
      document.getElementById('first-number').textContent = newFirst;
      document.getElementById('second-number').textContent = newSecond;
      
      updateTable(startIndex, endIndex, stat_r_keys);
      
      arrowsControl(totalRows, stat_r_keys);
    }
  };
  
  // Event listener para flecha derecha
  rightArrow.onclick = function() {
    if (currentSecondNumber < totalRows) {
      let newFirst = currentSecondNumber + 1;
      let newSecond = Math.min(newFirst + numberDisplayed - 1, totalRows);
      
      let startIndex = newFirst - 1;
      let endIndex = newSecond;
      
      document.getElementById('first-number').textContent = newFirst;
      document.getElementById('second-number').textContent = newSecond;
      
      updateTable(startIndex, endIndex, stat_r_keys);
      
      arrowsControl(totalRows, stat_r_keys);
    }
  };
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