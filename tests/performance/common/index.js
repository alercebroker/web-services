export function createUrl(url, objectClass, pageSize, objectList) {
  let completeUrl =
    url +
    "?ranking=1" +
    "&" +
    "classifier=lc_classifier" +
    "&" +
    "probability=0.5" +
    "&" +
    "ndet=10" +
    "&" +
    "order_by=probability" +
    "&" +
    "order_mode=DESC" +
    "&" +
    "page_size=" +
    pageSize +
    "&" +
    "class=" +
    objectClass;

  if (objectList && objectList instanceof Array) {
    let objectQuery = objectList.reduce(
      (acc, curr) => acc + "&oid=" + curr,
      ""
    );
    completeUrl = completeUrl + objectQuery;
  }

  return completeUrl;
}

export function getRandomElement(array) {
  const randomIndex = Math.floor(Math.random() * array.length);
  return array[randomIndex];
}
