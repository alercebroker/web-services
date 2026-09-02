export function create_dinamic_dropdown() {
    // se seleccionan todos los dropdowns
    for (const dropdown of document.querySelectorAll(".obj-select-wrapper")) {
        dropdown.addEventListener('click', function () {
            this.querySelector('.obj-select').classList.toggle('open');
        })
    }

    // Se incorporan funcionalidad a las opciones de los dropdowns
    for (const option of document.querySelectorAll(".obj-custom-option")) {
        option.addEventListener('click', () => {
            if (!option.classList.contains('obj-selected')) {

            option.parentNode.querySelector('.obj-custom-option.obj-selected').classList.remove('obj-selected');

            option.classList.add('obj-selected');

            option.closest('.obj-select').querySelector('.obj-select__trigger span').textContent = option.textContent;

            if (!option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.contains('dark:tw-text-[#EEEEEE]')) {
                option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.add('dark:tw-text-[#EEEEEE]')
            }


            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classes", option.getAttribute("data-classes"));
            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classifier", option.getAttribute("data-classifier"));
            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-version", option.getAttribute("data-version"));



            if (option.closest('.obj-select').querySelector('.obj-select__trigger span').id == "classifier") {
                document.getElementById("classifier").dispatchEvent(new Event("change"))
            }
            }
        })
    }
}


export function add_items_functionality() {

    let classifiers_button = document.getElementById("classifiers_selected")
    let classifiers_options = document.getElementById("classifiers_options")

    for (let item of classifiers_options.querySelectorAll(".obj-custom-option")) {

        item.addEventListener('click', () => {
            if (!item.classList.contains('obj-selected')) {

            item.parentNode.querySelector('.obj-custom-option.obj-selected').classList.remove('obj-selected');
            item.classList.add('obj-selected');

            classifiers_button.textContent = item.textContent;

            classifiers_button.setAttribute("data-classes", item.getAttribute("data-classes"));
            classifiers_button.setAttribute("data-classifier", item.getAttribute("data-classifier"));
            }

            draw_classes_options(item.getAttribute("data-classes"))
        })
    }


}


function draw_classes_options(classes) {
    let classes_options = document.getElementById("classes_options")
    let classes_arr = classes.split(",")

    classes_arr.forEach((class_name, index) => {
        let new_option = document.createElement("a")
        new_option.href = "#"
        new_option.textContent = class_name
        new_option.dataset.value = class_name

        classes_options.appendChild(new_option)
    })
    
}