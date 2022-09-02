Feature: Ask for a lightcurve data
  Background: initialize database

  Scenario Outline: ask for detections for object from ztf survey data
    Given there is detection for object ALERCE1 with id ZTF1 from telescope ZTF
    And there is detection for object ALERCE1 with id ZTF2 from telescope ZTF
    And there is detection for object ALERCE1 with id ATLAS1 from telescope ATLAS1
    And there is detection for object ALERCE1 with id ATLAS2 from telescope ATLAS2
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
