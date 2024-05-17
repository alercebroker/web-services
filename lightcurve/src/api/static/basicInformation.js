
let binaryDisc = 0;
let binaryLast = 0;
let binaryRaDec = 0;

export function changeDiscoveryValue(discoveryDateMGD,discoveryDateMJD){

    if (binaryDisc === 0) {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMGD;
        binaryDisc = 1;
    } else {
        document.getElementById("discoveryDate").innerHTML = discoveryDateMJD;
        binaryDisc = 0;
    }

};

export function changeLastValue(lastDetectionMGD,lastDetectionMJD){

    if (binaryLast === 0) {
        document.getElementById("lastDetection").innerHTML = lastDetectionMGD;
        binaryLast = 1;
    } else {
        document.getElementById("lastDetection").innerHTML = lastDetectionMJD;
        binaryLast = 0;
    }

};

export function changeRaDec(raDec,raDecTime){
    if (binaryRaDec === 0){
        document.getElementById("raDec").innerHTML = raDec;
        binaryRaDec = 1;
    } else {
        document.getElementById("raDec").innerHTML = raDecTime;
        binaryRaDec = 0;
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
    let month = date.getUTCMonth() + 1

    if (month < 10) {
        month = '0' + month
    }

    const day = date.getUTCDate()

    return year + '-' + month + '-' + day
}


export function transformRaDec(degrees) {
    
    let degreesPerHour = 360 / 24;
    let hours = Math.floor(degrees / degreesPerHour);
    let minutes = Math.floor((degrees % degreesPerHour) * 60 / degreesPerHour);
    let seconds = (((degrees % degreesPerHour) * 3600 / degreesPerHour) % 60).toFixed(3);

    let str = String(hours) + ':' + String(minutes) + ':' + String(seconds);

    return str
}