import moment from 'https://cdn.jsdelivr.net/npm/moment/+esm'

export function getUTCDate(date) {
  if (!date) return null
  const dateStr = date.toUTCString()
  return moment.utc(dateStr).toDate()
}

export function extractDate(datetime) {
  if (!datetime) return null
  return moment.utc(datetime).format('YYYY-MM-DD')
}

export function extractTime(datetime) {
  if (!datetime) return null
  return moment.utc(datetime).format('HH:mm')
}

export function convertToDate(date, time) {
  let strDate = date + '-' + time
  if (date && !time) {
    strDate = date + '-' + '00:00'
  }
  if (!date) {
    return null
  }
  return moment.utc(strDate, 'YYYY-MM-DD-HH:mm').toDate()
}

export function formatDate(date) {
  return moment.utc(date).format()
}
