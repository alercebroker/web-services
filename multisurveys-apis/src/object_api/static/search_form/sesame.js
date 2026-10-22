import {check_radio_consearch} from '../ui_helpers.js'
import {draw_notice_message} from '../draw_elements.js'

const SESAME_NOTICE = "sesame_notice"


export function get_sesame_object(object_name){

    document.getElementById(SESAME_NOTICE)?.remove()

    if (object_name.trim() == "") {
        show_sesame_notice("Write a target name to resolve.")
        return
    }

    let url = `https://cds.unistra.fr/cgi-bin/nph-sesame/-ox?${object_name}`

    fetch(url)
    .then((response) => response.text())
    .then((text) => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, "text/xml");

        let ra_node = xmlDoc.getElementsByTagName("jradeg")[0]
        let dec_node = xmlDoc.getElementsByTagName("jdedeg")[0]

        // Sesame answers an unknown name with a document without coordinates.
        if (ra_node === undefined || dec_node === undefined) {
            show_sesame_notice(`Sesame could not resolve "${object_name}". Check the name, or enter RA/Dec by hand.`)
            return
        }

        let ra_sesame = parseFloat(ra_node.childNodes[0].nodeValue)
        let dec_sesame = parseFloat(dec_node.childNodes[0].nodeValue)
        
        let [ra, dec] = check_radio_consearch(ra_sesame, dec_sesame)

        document.getElementById("ra_consearch").value = ra
        document.getElementById("dec_consearch").value = dec
        document.getElementById("radius_consearch").value = 1.5
    }).catch((error) => {
        console.error('Error fetching data:', error);
        show_sesame_notice("Sesame could not be reached. Try again later, or enter RA/Dec by hand.")
    });
}


// Shown under the conesearch filters, where the target name is.
function show_sesame_notice(message){
    document.getElementById("conesearch_filters_container").after(draw_notice_message(message, SESAME_NOTICE))
}