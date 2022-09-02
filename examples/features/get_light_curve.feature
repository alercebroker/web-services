Feature: Ask for a lightcurve data

  Scenario Outline: ask for detections for object from ztf survey data
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
