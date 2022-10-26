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
    // Load test for different query types (starts after smoke)
    transient_query: {
      executor: "constant-vus",
      exec: "objectQuery",
      startTime: "5m",
      vus: 10,
      duration: "5m",
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.SNIa, PAGE_SIZE: "20" },
    },
    variable_query: {
      executor: "constant-vus",
      exec: "objectQuery",
      startTime: "5m",
      vus: 10,
      duration: "5m",
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.CEP, PAGE_SIZE: "20" },
    },
    stochastic_query: {
      executor: "constant-vus",
      exec: "objectQuery",
      startTime: "5m",
      vus: 10,
      duration: "5m",
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.AGN, PAGE_SIZE: "20" },
    },
    // Retrieve one object at a time (concurrent with above + offset + 5 minutes)
    light_retrieve: {
      executor: "constant-vus",
      exec: "objectRetrieve",
      startTime: "6m",
      vus: 10,
      duration: "9m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.LIGHT },
    },
    medium_retrieve: {
      executor: "constant-vus",
      exec: "objectRetrieve",
      startTime: "6m",
      vus: 10,
      duration: "9m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.MEDIUM },
    },
    heavy_retrieve: {
      executor: "constant-vus",
      exec: "objectRetrieve",
      startTime: "6m",
      vus: 10,
      duration: "9m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.HEAVY },
    },
    // Detection list retrieval (last 10 minutes, non-concurrent with any above)
    light_detection_list: {
      executor: "constant-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "15m",
      vus: 10,
      duration: "10m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.LIGHT },
    },
    medium_detection_list: {
      executor: "constant-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "15m",
      vus: 10,
      duration: "10m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.MEDIUM },
    },
    heavy_detection_list: {
      executor: "constant-vus",
      exec: "objectDetectionsRetrieve",
      startTime: "15m",
      vus: 10,
      duration: "10m",
      gracefulStop: "0s",
      env: { OBJECT_TYPE: ObjectTypes.HEAVY },
    },
  },
  thresholds: {
    "group_duration{group:::retrieveObjectData}": ["p(90) < 2000"],
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
