
let binaryDisc = 0;
let binaryLast = 0;
let binaryRaDec = 0;

export function changeDiscoveryValue(discoveryDateMGD,discoveryDateMJD){
    if (binaryDisc === 1) {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMGD;
        binaryDisc = 0;
    } else {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMJD;
        binaryDisc = 1;
    }

};

export function changeLastValue(lastDetectionMGD,lastDetectionMJD){
    if (binaryLast === 1) {
        document.getElementById("lastDetection").innerHTML = lastDetectionMGD;
        binaryLast = 0;
    } else {
        document.getElementById("lastDetection").innerHTML = lastDetectionMJD;
        binaryLast = 1;
    }

};

export function changeRaDec(raDec,raDecTime){
    if (binaryRaDec === 1){
        document.getElementById("raDec").innerHTML = raDec;
        binaryRaDec = 0;
    } else {
        document.getElementById("raDec").innerHTML = raDecTime;
        binaryRaDec = 1;
    }
};

export function convertToDate(julian) {
    return new Date((Number(julian) - 2440587.5) * 86400000);
};

export function julianToGregorian(mjd) {

    if (mjd === undefined || mjd === null) {
        return null
    }

    const jd = Number(mjd) + 2400000
    const date = convertToDate(jd)
    console.log(date);
    const year = date.getUTCFullYear()
    let month = date.getUTCMonth()
    const day = date.getUTCDate()
    const hours = date.getUTCHours()
    const minutes = date.getUTCMinutes()
    const seconds = date.getUTCSeconds()
    const dayName = date.getUTCDay() 

    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    const days =  ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    
    return days[dayName] + ', ' + day + ' ' + months[month] + ' ' + year + ' ' + hours + ':' + minutes + ':' + seconds + ' UTC'
}


export function transformRaDec(degrees) {
    
    let degreesPerHour = 360 / 24;
    let hours = Math.floor(degrees / degreesPerHour);
    let minutes = Math.floor((degrees % degreesPerHour) * 60 / degreesPerHour);
    let seconds = (((degrees % degreesPerHour) * 3600 / degreesPerHour) % 60).toFixed(3);

    let str = String(hours) + ':' + String(minutes) + ':' + String(seconds);

    return str

}

export function url_modifier(ra,dec,object) {
           
    let url1 = 'https://www.legacysurvey.org/viewer/jpeg-cutout/?ra=' + String(ra)+'&dec='+ String(dec) + '&layer=ls-dr9&pixscale=0.1&bands=grz';
    document.getElementById('first-button').href = url1;

    let url2 = 'https://ned.ipac.caltech.edu/conesearch?search_type=Near+Position+Search&iau_style=liberal&objname=&coordinates=' + String(ra) + 'd,' + String(49.054) +'d&iau_name=&radius=0.17&in_csys=Equatorial&in_equinox=J2000&in_csys_IAU=Equatorial&in_equinox_IAU=B1950&z_constraint=Unconstrained&z_value1=&z_value2=&z_unit=z&ot_include=ANY&nmp_op=ANY&hconst=67.8&omegam=0.308&omegav=0.692&wmap=4&corr_z=1&out_csys=Same+as+Input&out_equinox=Same+as+Input&obj_sort=Distance+to+search+center&op=Go&form_build_id=form-a28snc2SSIQl3faGUe4otq7_NcjnMwxxxPoVxw5LHzg&form_id=conesearch'
    document.getElementById('second-button').href = url2

    let url3 = 'https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos='+String(ra)+ '+' + String(dec) + '&filter=color';
    document.getElementById('third-button').href = url3

    let url4 = 'https://skyserver.sdss.org/dr16/en/tools/chart/navi.aspx?ra='+ String(ra)+'8&dec='+ String(dec);
    document.getElementById('fourth-button').href = url4

    let url5 = 'https://simbad.u-strasbg.fr/simbad/sim-coo?Coord='+ String(ra) + '%20'+String(dec)+ '&Radius.unit=arcsec&Radius=10';
    document.getElementById('fifth-button').href = url5

    let url6 = 'https://www.wis-tns.org/search?ra='+ String(ra)+'&decl=' +String(dec) + '&radius=10&coords_unit=arcsec';
    document.getElementById('sixth-button').href = url6

    let url7 = 'https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c='+String(ra) + '+' + String(dec) + '&-c.rs=10&-out.add=_r&-sort=_r&-out.max=$4';
    document.getElementById('seventh-button').href = url7

    let  url8 = 'https://www.aavso.org/vsx/index.php?view=results.get&coords='+String(ra) + '+' + String(dec)+ '&format=d&size=10&geom=r&unit=3&order=9';
    document.getElementById('eighth-button').href = url8

    let url9 = 'https://findingchart.alerce.online/get_chart?oid='+ String(object) + '&candid=1007116353515015023'
    document.getElementById('find-button').href = url9
}