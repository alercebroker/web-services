import http from "k6/http";
import { check, fail, group, sleep } from "k6";
import { createUrl, getRandomElement } from "../common/index.js";

import objects from "../common/objects.consts.js"

const BASE_URL = "http://dev.api.alerce.online/alerts/v1/objects";

export function queryObjectsWithClass(objectClass, pageSize, objectList) {
  const url = createUrl(BASE_URL, objectClass, pageSize);

  group("queryObjects", () => {
    const objectsResponse = http.get(url);

    const isQuerySuccessful = check(objectsResponse, {
      "is query OK": (r) => r.status === 200,
    });
  });
  sleep(2);
}

export function retrieveObjectData(objectType) {
  const oid = objects[objectType][0];

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
  sleep(2);
}

export function retrieveDetectionsList(objectType) {
  const objectPool = objects[objectType];

  group('retrieveDetectionsList', (_) => {
    for (var i=0; i < objectPool.length; i++){
      const oid = objectPool[i]
      const detectionsResponse = http.get(BASE_URL + '/' + oid + '/detections');

      check(detectionsResponse, {
        "detections retrieved successfully": (r) => r.status === 200,
      });
    }
  });
}
