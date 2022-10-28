import {
  queryObjectsWithClass,
  retrieveObjectData,
  retrieveDetectionsList
} from "../user_actions/index.js";

export function frontendScenario(objectType, objectClass, pageSize, objectSeed) {
  queryObjectsWithClass(objectClass, pageSize);
  retrieveObjectData(objectType, objectSeed);
}

export function directQueryScenario(objectType) {
  retrieveObjectData(objectType);
}

export function objectQueryScenario(objectClass, pageSize) {
  queryObjectsWithClass(objectClass, pageSize);
}

export function detectionsQueryScenario(objectType) {
  retrieveDetectionsList(objectType);
}