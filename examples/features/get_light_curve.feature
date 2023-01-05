Feature: Ask for a lightcurve data

  Scenario Outline: ask for lightcurves
    Given there are detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF1   | ZTF     |
      | c2     | ZTF2   | ZTF     |
      | c3     | ATLAS1 | ATLAS-1 |
      | c4     | ATLAS2 | ATLAS-2 |
    And there are non_detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF3   | ZTF     |
      | c2     | ATLAS3 | ATLAS-1 |
    When request lightcurve for object ALERCE1 in <survey> survey as <user>
    Then retrieve detections with identifiers: <detections>; and non detections with identifiers: <non_detections>
    Examples:
      | user  | survey | detections              | non_detections |
      | admin | ZTF    | ZTF1,ZTF2               | ZTF3           |
      | admin | ATLAS  | ATLAS1,ATLAS2           | ATLAS3         |
      | admin | all    | ZTF1,ZTF2,ATLAS1,ATLAS2 | ZTF3,ATLAS3    |
      | other | ZTF    | ZTF1,ZTF2               | ZTF3           |
      | other | ATLAS  | none                    | none           |
      | other | all    | ZTF1,ZTF2               | ZTF3           |

  Scenario Outline: ask for object detections
    Given there are detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF1   | ZTF     |
      | c2     | ZTF2   | ZTF     |
      | c3     | ATLAS1 | ATLAS-1 |
      | c4     | ATLAS2 | ATLAS-2 |
    When request detections for object ALERCE1 in <survey> survey as <user>
    Then retrieve results with identifiers: <oids>
    Examples:
      | user  | survey | oids                    |
      | admin | ZTF    | ZTF1,ZTF2               |
      | admin | ATLAS  | ATLAS1,ATLAS2           |
      | admin | all    | ZTF1,ZTF2,ATLAS1,ATLAS2 |
      | other | ZTF    | ZTF1,ZTF2               |
      | other | ATLAS  | none                    |
      | other | all    | ZTF1,ZTF2               |

  Scenario Outline: ask for object non-detections
    Given there are non_detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF1   | ZTF     |
      | c2     | ZTF2   | ZTF     |
      | c3     | ATLAS1 | ATLAS-1 |
      | c4     | ATLAS2 | ATLAS-2 |
    When request non detections for object ALERCE1 in <survey> survey as <user>
    Then retrieve results with identifiers: <oids>
    Examples:
      | user  | survey | oids                    |
      | admin | ZTF    | ZTF1,ZTF2               |
      | admin | ATLAS  | ATLAS1,ATLAS2           |
      | admin | all    | ZTF1,ZTF2,ATLAS1,ATLAS2 |
      | other | ZTF    | ZTF1,ZTF2               |
      | other | ATLAS  | none                    |
      | other | all    | ZTF1,ZTF2               |

  Scenario Outline: ask for first detection of object
    Given there are detections for object ALERCE1 with following parameters
      | candid | oid    | tid     | mjd |
      | c1     | ZTF2   | ZTF     | 2.5 |
      | c2     | ZTF1   | ZTF     | 2.0 |
      | c3     | ATLAS2 | ATLAS-1 | 1.5 |
      | c4     | ATLAS1 | ATLAS-2 | 1.0 |
    When request first detection for object ALERCE1 in <survey> survey as <user>
    Then retrieve results with identifiers: <oids>
    Examples:
      | user  | survey | oids   |
      | admin | ZTF    | ZTF1   |
      | admin | ATLAS  | ATLAS1 |
      | admin | all    | ATLAS1 |
      | other | ZTF    | ZTF1   |
      | other | ATLAS  | none   |
#      | other | all    | ZTF1   |

  Scenario Outline: ask for first non-detection of object
    Given there are non_detections for object ALERCE1 with following parameters
       | candid | oid    | tid     | mjd |
       | c1     | ZTF2   | ZTF     | 2.5 |
       | c2     | ZTF1   | ZTF     | 2.0 |
       | c3     | ATLAS2 | ATLAS-1 | 1.5 |
       | c4     | ATLAS1 | ATLAS-1 | 1.0 |
    When request first non detection for object ALERCE1 in <survey> survey as <user>
    Then retrieve results with identifiers: <oids>
    Examples:
      | user  | survey | oids   |
      | admin | ZTF    | ZTF1   |
      | admin | ATLAS  | ATLAS1 |
      | admin | all    | ATLAS1 |
      | other | ZTF    | ZTF1   |
      | other | ATLAS  | none   |
#      | other | all    | ZTF1   |

  Scenario Outline: request lightcurves for non-existing objects
    Given there are detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF1   | ZTF     |
      | c2     | ATLAS1 | ATLAS-1 |
    And there are non_detections for object ALERCE1 with following parameters
      | candid | oid    | tid     |
      | c1     | ZTF2   | ZTF     |
      | c2     | ATLAS2 | ATLAS-1 |
    When request <endpoint> for object ALERCE2 in <survey> survey as <user>
    Then retrieve error code 404
    Examples:
      | endpoint       | user  | survey |
      | detections     | admin | ZTF    |
      | detections     | admin | ATLAS  |
      | detections     | admin | all    |
      | detections     | other | ZTF    |
      | detections     | other | ATLAS  |
      | detections     | other | all    |
      | non detections | admin | ZTF    |
      | non detections | admin | ATLAS  |
      | non detections | admin | all    |
      | non detections | other | ZTF    |
      | non detections | other | ATLAS  |
      | non detections | other | all    |
      | lightcurve     | admin | ZTF    |
      | lightcurve     | admin | ATLAS  |
      | lightcurve     | admin | all    |
      | lightcurve     | other | ZTF    |
      | lightcurve     | other | ATLAS  |
      | lightcurve     | other | all    |
