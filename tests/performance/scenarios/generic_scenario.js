import http from "k6/http";
import { check, fail, group, sleep } from "k6";

import objects from "./objects.consts.js";

const BASE_URL = "http://dev.api.alerce.online/alerts/v1/objects";

function createUrl(objectClass, pageSize) {
  return (
    BASE_URL +
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
    objectClass
  );
}

function getRandomElement(array) {
  const randomIndex = Math.floor(Math.random() * array.length);
  return array[randomIndex];
}

export function frontendScenario(objectType, objectClass, pageSize) {
  const url = createUrl(objectClass, pageSize);
  const objectsResponse = http.get(url);

  const isQuerySuccessful = check(objectsResponse, {
    "is query OK": (r) => r.status === 200,
  });

  if (!isQuerySuccessful)
    fail(`[Objects ${objectClass} query] Failed with status ${objectsResponse.status}`)

  sleep(2);

  const objectPool = objects[objectType];
  const oid = getRandomElement(objectPool);

  group('retrieveObjectData', (_) => {
    const responses = http.batch([
      ['GET', BASE_URL + '/' + oid + '/lightcurve'],
      ['GET', BASE_URL + '/' + oid + '/magstats'],
      ['GET', BASE_URL + '/' + oid + '/probabilities'],
    ]);

    check(responses[0], {'lightcurve status is 200': (r) => r.status === 200});
    check(responses[1], {'magstats status is 200': (r) => r.status === 200});
    check(responses[2], {'probabilities status is 200': (r) => r.status === 200});
  });
}
