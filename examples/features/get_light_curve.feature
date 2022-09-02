Feature: Ask for a lightcurve data

  Scenario Outline: ask for object detections
    Given there are detections in database with following parameters
      | aid     | oid    | tid     |
      | ALERCE1 | ZTF1   | ZTF     |
      | ALERCE1 | ZTF2   | ZTF     |
      | ALERCE1 | ATLAS1 | ATLAS-1 |
      | ALERCE1 | ATLAS2 | ATLAS-2 |
    When request detections for object ALERCE1 in <survey> survey <has permission>
    Then retrieve detections with identifiers <oids>
    Examples:
      | has permission     | survey | oids                    |
      | with permission    | ZTF    | ZTF1,ZTF2               |
      | with permission    | ATLAS  | ATLAS1,ATLAS2           |
      | with permission    | both   | ZTF1,ZTF2,ATLAS1,ATLAS2 |
      | without permission | ZTF    | ZTF1,ZTF2               |
      | without permission | ATLAS  | none                    |
      | without permission | both   | ZTF1,ZTF2               |

  Scenario Outline: ask first detection only
    Given there are detections in database with following parameters
      | aid     | oid    | tid     | mjd |
      | ALERCE1 | ZTF1   | ZTF     | 2.0 |
      | ALERCE1 | ZTF2   | ZTF     | 2.5 |
      | ALERCE1 | ATLAS1 | ATLAS-1 | 1.0 |
      | ALERCE1 | ATLAS1 | ATLAS-1 | 1.5 |
    When request first detections for object ALERCE1 in <survey> survey <has permission>
    Then retrieve detections with identifiers <oids>
    Examples:
      | has permission     | survey | oids   |
      | with permission    | ZTF    | ZTF1   |
      | with permission    | ATLAS  | ATLAS1 |
      | with permission    | both   | ATLAS1 |
      | without permission | ZTF    | ZTF1   |
      | without permission | ATLAS  | none   |
#      | without permission | both   | ZTF1   |
