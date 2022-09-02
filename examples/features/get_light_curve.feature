Feature: Ask for a lightcurve data

  Scenario Outline: ask for object detections
    Given there are <endpoint> in database with following parameters
      | aid     | oid    | tid     |
      | ALERCE1 | ZTF1   | ZTF     |
      | ALERCE1 | ZTF2   | ZTF     |
      | ALERCE1 | ATLAS1 | ATLAS-1 |
      | ALERCE1 | ATLAS2 | ATLAS-2 |
    When request <endpoint> for object ALERCE1 in <survey> survey <has permission>
    Then retrieve results with identifiers <oids>
    Examples:
      | endpoint       | has permission     | survey | oids                    |
      | detections     | with permission    | ZTF    | ZTF1,ZTF2               |
      | detections     | with permission    | ATLAS  | ATLAS1,ATLAS2           |
      | detections     | with permission    | both   | ZTF1,ZTF2,ATLAS1,ATLAS2 |
      | detections     | without permission | ZTF    | ZTF1,ZTF2               |
      | detections     | without permission | ATLAS  | none                    |
      | detections     | without permission | both   | ZTF1,ZTF2               |
      | non_detections | with permission    | ZTF    | ZTF1,ZTF2               |
      | non_detections | with permission    | ATLAS  | ATLAS1,ATLAS2           |
      | non_detections | with permission    | both   | ZTF1,ZTF2,ATLAS1,ATLAS2 |
      | non_detections | without permission | ZTF    | ZTF1,ZTF2               |
      | non_detections | without permission | ATLAS  | none                    |
      | non_detections | without permission | both   | ZTF1,ZTF2               |

  Scenario Outline: ask first detection only
    Given there are detections in database with following parameters
      | aid     | oid    | tid     | mjd |
      | ALERCE1 | ZTF1   | ZTF     | 2.0 |
      | ALERCE1 | ZTF2   | ZTF     | 2.5 |
      | ALERCE1 | ATLAS1 | ATLAS-1 | 1.0 |
      | ALERCE1 | ATLAS1 | ATLAS-1 | 1.5 |
    When request first detections for object ALERCE1 in <survey> survey <has permission>
    Then retrieve results with identifiers <oids>
    Examples:
      | has permission     | survey | oids   |
      | with permission    | ZTF    | ZTF1   |
      | with permission    | ATLAS  | ATLAS1 |
      | with permission    | both   | ATLAS1 |
      | without permission | ZTF    | ZTF1   |
      | without permission | ATLAS  | none   |
#      | without permission | both   | ZTF1   |
