import exec from "k6/execution";
import {
  frontendScenario,
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
      executor: "ramping-vus",
      exec: "fullScenario",
      startVUs: 10,
      stages: [
        {duration: "5m", target: 10},
        {duration: "5m", target: 50},
        {duration: "5m", target: 100},
        {duration: "5m", target: 150},
        {duration: "5m", target: 200},
        {duration: "5m", target: 250},
        {duration: "5m", target: 300},
      ],
      gracefulStop: "0s",
      env: { CLASS: ClassTypes.SNIa, OBJECT_TYPE: ObjectTypes.MEDIUM, PAGE_SIZE: "10" }
    },
  },
  thresholds: {
    checks: [
      {
        threshold: 'rate>0.90',
        abortOnFail: true,
        delayAbortEval: '10s',
      }
    ],
    "group_duration{group:::retrieveObjectData}": ["p(90) < 2000"],
    "group_duration{group:::queryObjects}": ["p(90) < 2000"],
  },
};

export function fullScenario (){
  const { CLASS, OBJECT_TYPE, PAGE_SIZE } = __ENV;
  frontendScenario(OBJECT_TYPE, CLASS, PAGE_SIZE);
}
