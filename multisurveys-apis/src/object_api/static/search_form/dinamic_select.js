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