import exec from "k6/execution";
import { frontendScenario } from "./scenarios/generic_scenario.js";

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
    snia_objects_ramping: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: 100 },
        { duration: "1m", target: 30 },
        { duration: "5m", target: 0 },
      ],
      gracefulRampdown: "0s",
      env: { CLASS: ClassTypes.SNIa, PAGE_SIZE: "20" },
    },
    cep_objects_ramping: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: 100 },
        { duration: "1m", target: 30 },
        { duration: "5m", target: 0 },
      ],
      gracefulRampdown: "0s",
      env: { CLASS: ClassTypes.CEP, PAGE_SIZE: "20" },
    },
    agn_objects_ramping: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "1m", target: 100 },
        { duration: "1m", target: 30 },
        { duration: "5m", target: 0 },
      ],
      gracefulRampdown: "0s",
      env: { CLASS: ClassTypes.AGN, PAGE_SIZE: "20" },
    },
  },
  thresholds: {
    "group_duration{group:::retrieveObjectData}": ["p(90) < 2000"],
    "group_duration{group:::queryObjects}": ["p(90) < 2000"],
  },
};

export default () => {
  const { CLASS, OBJECT_TYPE, PAGE_SIZE } = __ENV;
  if (!OBJECT_TYPE || !Object.values(ObjectTypes).includes(OBJECT_TYPE)) {
    exec.test.abort(
      "[BAD ENV VARIABLES] Usage: k6 run -e OBJECT_TYPE={light | medium | heavy } script.js"
    );
  }
  frontendScenario(OBJECT_TYPE, CLASS, +PAGE_SIZE);
};
