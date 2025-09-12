import { get_radar_config } from "./radar_config.js"


class radarCreator{
    constructor(config, container, classes, probabilities){
        this.config = config
        this.ctx = container
        this.classes = classes
        this.probabilities = probabilities
        this.max_value = 0
        this.scale = 0
        this.mychart = new Chart(this.ctx, this.config)
    }

    set_max_value(){
        this.max_value = Math.max.apply(Math, this.probabilities)
    }

    set_scale(){
        this.scale = (this.max_value/3)
    }

    update_chart(){
        this.remove_data()
        this.update_data()
        this.is_dark();
    }

    update_data(){
        this.mychart.data.labels.push(...this.classes);
        this.mychart.data.datasets.forEach((dataset) => {
            dataset.data.push(...this.probabilities);
        });

        this.set_max_value()
        this.set_scale()
        this.update_scale()

        this.mychart.update();
    }

    update_scale(){
        this.mychart.config.options.scales.r.ticks.stepSize = this.scale
        this.mychart.config.options.scales.r.max = this.max_value
    }

    remove_data(){
        this.mychart.data.labels.length = 0;
        this.mychart.data.datasets.forEach((dataset) => {
            dataset.data.length = 0;
        });

        this.mychart.update();
    }

    destroy_chart(){
        this.mychart.destroy();
    }

    is_dark(){
        if(document.getElementById("probabilities-app").classList.contains("tw-dark")){
            this.mychart.config.options.scales.r.backgroundColor = 'rgba(245, 245, 245, 0.2)'
            this.mychart.config.options.scales.r.angleLines.color = '#F5F5F5'
            this.mychart.config.options.scales.r.grid.color = '#F5F5F5'
            this.mychart.config.options.scales.r.pointLabels.color = '#F5F5F5'
            
            this.mychart.update();
        }
    }
}

export function init(){
    let raw_data = JSON.parse(document.getElementById("probabilities-data").text);
    let raw_group_prob_dict = raw_data.group_prob_dict
    let taxonomy_and_probabilities = get_taxonomy_dict(raw_group_prob_dict)
    let classifiers_data_reverse= reverse_data(taxonomy_and_probabilities)

    let custom_select = document.querySelector(".select-wrapper")
    let classifier_selected = document.querySelector('.custom-option.selected').getAttribute("data-value")
    let classifier_selected_data = classifiers_data_reverse[classifier_selected]
    let classifier_data_dict = get_probabilities_and_classes_dict(classifier_selected_data)

    let ctx = document.getElementById('myChart');
    let config = get_radar_config()
    let radar = new radarCreator(
        config, 
        ctx, 
        classifier_data_dict['classes'], 
        classifier_data_dict['probabilities']
    )

    radar.update_chart()

    custom_select.addEventListener('click', () => {
        custom_select.querySelector('.select').classList.toggle('open');
    })

    for(const option of document.querySelectorAll(".custom-option")){
        option.addEventListener('click', () => {
            if(!option.classList.contains('selected')){
                option.parentNode.querySelector('.custom-option.selected').classList.remove('selected');
                option.classList.add('selected');
                option.closest('.select').querySelector('.select__trigger span').textContent = option.textContent;


                classifier_selected_data = classifiers_data_reverse[option.getAttribute("data-value")]
                classifier_data_dict = get_probabilities_and_classes_dict(classifier_selected_data)

                radar.destroy_chart()
                radar = new radarCreator(
                    config, 
                    ctx, 
                    classifier_data_dict['classes'], 
                    classifier_data_dict['probabilities']
                )
                radar.update_chart()

            }
        })
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

function get_taxonomy_dict(probabilities_dict){
    let response_dict = {}
    for (let [key, values] of Object.entries(probabilities_dict)){
        let classes_with_probabilities = values.map((element) => {
            return [element.class_name, element.probability]
        })

        response_dict[key] = classes_with_probabilities
    }

    return response_dict
}

function reverse_data(raw_tax){
    let aux_arr = []

    Object.keys(raw_tax).forEach((key) => {
        aux_arr = raw_tax[key].map((item, idx) => {
            if (idx == 0) {
                return item
            } else {
                let classes = raw_tax[key]
                let inverse_position = classes.length - idx

                return classes[inverse_position]
            }
        })

        raw_tax[key] = aux_arr
    })

    return raw_tax
}


function get_probabilities_and_classes_dict(classifier_probabilities){
    let classes_array = classifier_probabilities.map((class_name) => {return class_name[0]})
    let probabilities_array = classifier_probabilities.map((probability) => {return probability[1]}) 

    return {"classes": classes_array, "probabilities": probabilities_array}
}
