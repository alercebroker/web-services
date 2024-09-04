
let binaryDisc = 0;
let binaryLast = 0;
let binaryRaDec = 0;

export function changeDiscoveryValue(discoveryDateMGD,discoveryDateMJD){
    if (binaryDisc === 1) {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMGD;
        document.getElementById("textDiscoveryToolTip").innerText = "View MJD"
        binaryDisc = 0;
    } else {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMJD;
        document.getElementById("textDiscoveryToolTip").innerText = "View date"
        binaryDisc = 1;
    }

};

export function changeLastValue(lastDetectionMGD,lastDetectionMJD){
    if (binaryLast === 1) {
        document.getElementById("lastDetection").innerHTML = lastDetectionMGD;
        document.getElementById("textLastDetectionToolTip").innerHTML = "View MJD"
        binaryLast = 0;
    } else {
        document.getElementById("lastDetection").innerHTML = lastDetectionMJD;
        document.getElementById("textLastDetectionToolTip").innerHTML = "View date"
        binaryLast = 1;
    }

};

export function changeRaDec(raDec,raDecTime){
    if (binaryRaDec === 1){
        document.getElementById("raDec").innerHTML = raDec;
        document.getElementById("textRaDecToolTip").innerHTML = "View H:M:S"
        binaryRaDec = 0;
    } else {
        document.getElementById("raDec").innerHTML = raDecTime;
        document.getElementById("textRaDecToolTip").innerHTML = "View Degrees"
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


export function transformDec(dec){
    const sign = dec < 0 ? '-' : '+'
    dec = Math.abs(dec)
    const deg = Math.floor(dec)
    const decM = Math.abs(Math.floor((dec - deg) * 60))
    const decS = ((Math.abs((dec - deg) * 60) - decM) * 60).toFixed(2)
    dec = `${sign}${deg}:${decM}:${decS}`

    return dec
}

export function transformRa(degrees) {
    let degreesPerHour = 360 / 24;
    let hours = Math.floor(degrees / degreesPerHour);
    let minutes = Math.floor((degrees % degreesPerHour) * 60 / degreesPerHour);
    let seconds = (((degrees % degreesPerHour) * 3600 / degreesPerHour) % 60).toFixed(3);

    let str = String(hours) + ':' + String(minutes) + ':' + String(seconds);

    return str

}

export function setMenuUrl(ra,dec,candid,object) {

    const urlDict = {'desi-button': `https://www.legacysurvey.org/viewer/jpeg-cutout/?ra=${ra}&dec=${dec}&layer=ls-dr10&pixscale=0.1&bands=grz`,
                     'ned-button': `https://ned.ipac.caltech.edu/conesearch?search_type=Near+Position+Search&iau_style=liberal&objname=&coordinates=${ra}d,${dec}d&iau_name=&radius=0.17&in_csys=Equatorial&in_equinox=J2000&in_csys_IAU=Equatorial&in_equinox_IAU=B1950&z_constraint=Unconstrained&z_value1=&z_value2=&z_unit=z&ot_include=ANY&nmp_op=ANY&hconst=67.8&omegam=0.308&omegav=0.692&wmap=4&corr_z=1&out_csys=Same+as+Input&out_equinox=Same+as+Input&obj_sort=Distance+to+search+center&op=Go&form_build_id=form-a28snc2SSIQl3faGUe4otq7_NcjnMwxxxPoVxw5LHzg&form_id=conesearch`,
                     'pan-button': `https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=${ra}+${dec}&filter=color`,
                    'sdss-button': `https://skyserver.sdss.org/dr16/en/tools/chart/navi.aspx?ra=${ra}8&dec=${dec}`,
                    'simbad-button':`https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=${ra}%20${dec}&Radius.unit=arcsec&Radius=10`,
                    'tns-button': `https://www.wis-tns.org/search?ra=${ra}&decl=${dec}&radius=10&coords_unit=arcsec`,
                    'viz-button': `https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c=${ra}+${dec}&-c.rs=10&-out.add=_r&-sort=_r&-out.max=$4`,
                    'vsx-button': `https://www.aavso.org/vsx/index.php?view=results.get&coords=${ra}+${dec}&format=d&size=10&geom=r&unit=3&order=9`,
                    'find-button': `https://findingchart.alerce.online/get_chart?oid=${object}&candid=${candid}`
                    }

    for (let button in urlDict){
        document.getElementById(button).href = urlDict[button];
    };
}