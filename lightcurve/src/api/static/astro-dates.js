var DAY = 86400000;
var HALF_DAY = DAY / 2;
var UNIX_EPOCH_JULIAN_DATE = 2440587.5;
var UNIX_EPOCH_JULIAN_DAY = 2440587;


function convertToDate(julian) {
  return new Date((Number(julian) - UNIX_EPOCH_JULIAN_DATE) * DAY);
};


/**
 * receives date in julian format and convert in gregorian format
 * @param MJD:date in julian format
 * @returns {string} : date in gregorian format
 */
function jdToGregorian(mjd) {
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

/**
 * receives date in gregorian format and convert in julian format
 * @param dateObj:date Object
 * @returns {number} : date in jualian format
 */
function gregorianToJd(dateObj) {
  if (dateObj === null) {
    return null
  }
  const mjulianDate = dateObj / 86400000 + 40587
  return mjulianDate
}

function jdToDate(mjd) {
  if (mjd === undefined || mjd === null || mjd === '') {
    return null
  }
  const date = (mjd - 40587) * 86400000
  return new Date(date)
}

/* Based in: http://www.bdnyc.org/2012/10/decimal-deg-to-hms/ */
function raDectoHMS(ra, dec) {
  if (dec) {
    const sign = dec < 0 ? '-' : '+'
    dec = Math.abs(dec)
    const deg = Math.floor(dec)
    const decM = Math.abs(Math.floor((dec - deg) * 60))
    const decS = ((Math.abs((dec - deg) * 60) - decM) * 60).toFixed(2)
    dec = `${sign}${deg}:${decM}:${decS}`
  }
  if (ra) {
    const sign = ra < 0 ? '-' : '\xA0'
    ra = Math.abs(ra)
    const raH = Math.floor(ra / 15)
    const raM = Math.floor((ra / 15 - raH) * 60)
    const raS = (((ra / 15 - raH) * 60 - raM) * 60).toFixed(3)
    ra = `${sign}${raH}:${raM}:${raS}`
  }
  return `${ra} ${dec}`
}

export { gregorianToJd, jdToDate, jdToGregorian, raDectoHMS };

