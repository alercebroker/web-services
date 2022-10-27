import exec from "k6/execution";
import {
  frontendScenario,
  objectQueryScenario,
  directQueryScenario,
  detectionsQueryScenario
} from "./scenarios/generic_scenario.js";

const ObjectTypes = {
  LIGHT: "light",
  MEDIUM: "medium",
  HEAVY: "heavy",
};

const ClassTypes = {
  SNIa: "SNIa",
  CEP: "CEP",
  AGN: "AGN",
};

const VU_NORMAL = 10;
const VU_PEAK = 50;

export const options = {
  scenarios: {
    // Smoke test (first 5 minutes)
    smoke_test: {
      executor: "constant-vus",
      exec: "fullScenario",
      duration: "5m",
      vus: 10,
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.SNIa, OBJECT_TYPE: ObjectTypes.MEDIUM, PAGE_SIZE: "10" }
    },
    // Stress test for different query types (starts after smoke)
    transient_query: {
      executor: "ramping-vus",
      exec: "objectQuery",
      startTime: "5m",
      startVUs: 10,
      stages: [
        {duration: "1m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "3m", target: VU_NORMAL},
        {duration: "1m", target: 0}
      ],
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.SNIa, PAGE_SIZE: "20" },
    },
    variable_query: {
      executor: "ramping-vus",
      exec: "objectQuery",
      startTime: "5m",
      startVUs: 10,
      stages: [
        {duration: "2m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "2m", target: VU_NORMAL},
        {duration: "1m", target: 0}
      ],
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.CEP, PAGE_SIZE: "20" },
    },
    stochastic_query: {
      executor: "ramping-vus",
      exec: "objectQuery",
      startTime: "5m",
      startVUs: 10,
      stages: [
        {duration: "3m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "1m", target: VU_NORMAL},
        {duration: "1m", target: 0}
      ],
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.AGN, PAGE_SIZE: "20" },
    },
    // Retrieve one object at a time (concurrent with above + offset + 6 minutes)
    light_retrieve: {
      executor: "ramping-vus",
      exec: "objectRetrieve",
      startTime: "5m",
      startVUs: 0,
      stages: [
        {duration: "1m", target: VU_NORMAL},
        {duration: "5m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "5m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.LIGHT },
    },
    medium_retrieve: {
      executor: "ramping-vus",
      exec: "objectRetrieve",
      startTime: "5m",
      startVUs: 0,
      stages: [
        {duration: "1m", target: VU_NORMAL},
        {duration: "6m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "4m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.MEDIUM },
    },
    heavy_retrieve: {
      executor: "ramping-vus",
      exec: "objectRetrieve",
      startTime: "5m",
      startVUs: 0,
      stages: [
        {duration: "1m", target: VU_NORMAL},
        {duration: "7m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "3m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.HEAVY },
    },
    // Detection list retrieval (last 14 minutes, non-concurrent with any above)
    light_detection_list: {
      executor: "ramping-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "17m",
      startVUs: 10,
      stages: [
        {duration: "3m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "10m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.LIGHT },
    },
    medium_detection_list: {
      executor: "ramping-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "17m",
      startVUs: 10,
      stages: [
        {duration: "5m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "8m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.MEDIUM },
    },
    heavy_detection_list: {
      executor: "ramping-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "17m",
      startVUs: 10,
      stages: [
        {duration: "7m", target: VU_NORMAL},
        {duration: "30s", target: VU_PEAK},
        {duration: "30s", target: VU_NORMAL},
        {duration: "6m", target: VU_NORMAL},
      ],
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.HEAVY },
    },
  },
  thresholds: {
    checks: ['rate>0.95'],
    "group_duration{group:::retrieveObjectData}": ["p(90) < 2000"],
    "group_duration{group:::retrieveDetectionsList}": ["p(90) < 30000"],
    "group_duration{group:::queryObjects}": ["p(90) < 2000"],
  },
};

export function fullScenario (){
  const { CLASS, OBJECT_TYPE, PAGE_SIZE } = __ENV;
  frontendScenario(OBJECT_TYPE, CLASS, PAGE_SIZE);
}

export function objectQuery (){
  const { CLASS, PAGE_SIZE } = __ENV;
  objectQueryScenario(CLASS, PAGE_SIZE);
};

export function objectRetrieve (){
  const { OBJECT_TYPE } = __ENV;
  directQueryScenario(OBJECT_TYPE);
};

export function objectDetectionsRetrieve (){
  const { OBJECT_TYPE } = __ENV;
  detectionsQueryScenario(OBJECT_TYPE);
};
