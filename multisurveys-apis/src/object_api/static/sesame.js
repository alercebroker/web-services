import {check_radio_consearch} from './ui_helpers.js'


export function get_sesame_object(object_name){

    let url = `https://cds.unistra.fr/cgi-bin/nph-sesame/-ox?${object_name}`

    fetch(url)
    .then((response) => response.text())
    .then((text) => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(text, "text/xml");

        let ra_sesame = parseFloat(xmlDoc.getElementsByTagName("jradeg")[0].childNodes[0].nodeValue)
        let dec_sesame = parseFloat(xmlDoc.getElementsByTagName("jdedeg")[0].childNodes[0].nodeValue)
        
        let [ra, dec] = check_radio_consearch(ra_sesame, dec_sesame)

        document.getElementById("ra_consearch").value = ra
        document.getElementById("dec_consearch").value = dec
        document.getElementById("radius_consearch").value = 1.5
    }).catch((error) => {
        console.error('Error fetching data:', error);
    });
}