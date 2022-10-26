import {
  queryObjectsWithClass,
  retrieveObjectData,
  retrieveDetectionsList
} from "../user_actions/index.js";

export function frontendScenario(objectType, objectClass, pageSize) {
  queryObjectsWithClass(objectClass, pageSize);
  retrieveObjectData(objectType);
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