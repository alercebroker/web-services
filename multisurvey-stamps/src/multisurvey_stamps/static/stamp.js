
const imagesList = ['bird.jpg', 'cat.jpg', 'elephant.jpg'];

const imageParser = {
    'bird': 'bird.jpg',
    'cat': 'cat.jpg',
    'elephant': 'elephant.jpg',
};

const stampsIds = ['science', 'template', 'difference']

export function initStamp(){
    // Make function available globally for onclick handlers
    window.showNewImage = showNewImage;
};


export function showNewImage(imageName){
  console.log(imageName);
  for (let stamp of stampsIds){
      document.getElementById(`${stamp}-image`).src = `../static/stamps/${imageParser[imageName]}`;
  };

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