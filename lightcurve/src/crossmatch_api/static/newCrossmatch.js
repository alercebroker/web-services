
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
  
export function initCrossmatch() {
    // Add event listeners to all buttons with the 'show-table-btn' class
    document.querySelectorAll('.show-table-btn').forEach(button => {
        button.addEventListener('click', function() {
            const key = this.getAttribute('data-key');
            showTable(key);
        });
    });


}

export function showTable(key) {
    const table = document.getElementById(`table-${key}`);
    if (table) {
        table.style.display = table.style.display === 'block' ? 'none' : 'block';
    }
}