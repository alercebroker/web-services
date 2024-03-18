import http from "k6/http";
import { check, fail, group, sleep } from "k6";
import { Counter } from "k6/metrics";
import { createUrl, getRandomElement } from "../common/index.js";

import objects from "../common/objects.consts.js";

//const BASE_URL = "http://dev.api.alerce.online/alerts/v1/objects";
const BASE_URL =
  "http://k8s-default-wsingres-bb900d3478-141217347.us-east-1.elb.amazonaws.com/objects";
const errors = new Counter("errors");

function checkError(checkSuccessful) {
  if (!checkSuccessful) errors.add(1);
}

export function queryObjectsWithClass(objectClass, pageSize, objectList) {
  const url = createUrl(BASE_URL, objectClass, pageSize);

  group("queryObjects", () => {
    const objectsResponse = http.get(url);

    const isQuerySuccessful = check(objectsResponse, {
      "is query OK": (r) => r.status === 200,
    });
    checkError(isQuerySuccessful);
  });
  sleep(2);
}

export function retrieveObjectData(objectType, seed) {
  const objectIndex = seed ? seed % 5 : 0;
  const oid = objects[objectType][objectIndex];

  group("retrieveObjectData", (_) => {
    const responses = http.batch([
      ["GET", BASE_URL + "/" + oid + "/lightcurve"],
      ["GET", BASE_URL + "/" + oid + "/magstats"],
      ["GET", BASE_URL + "/" + oid + "/probabilities"],
    ]);

    const isLightCurveSuccessful = check(responses[0], {
      "lightcurve status is 200": (r) => r.status === 200,
    });
    const isMagStatsSuccessful = check(responses[1], {
      "magstats status is 200": (r) => r.status === 200,
    });
    const isProbabilitiesSuccessful = check(responses[2], {
      "probabilities status is 200": (r) => r.status === 200,
    });

    checkError(isLightCurveSuccessful);
    checkError(isProbabilitiesSuccessful);
    checkError(isMagStatsSuccessful);
  });
  sleep(2);
}

export function retrieveDetectionsList(objectType) {
  const objectPool = objects[objectType];

  group("retrieveDetectionsList", (_) => {
    for (let i = 0; i < objectPool.length; i++) {
      const oid = objectPool[i];
      const detectionsResponse = http.get(BASE_URL + "/" + oid + "/detections");

      const areDetectionsSuccessful = check(detectionsResponse, {
        "detections retrieved successfully": (r) => r.status === 200,
      });
      errors.add(!areDetectionsSuccessful);
    }
  });
}
