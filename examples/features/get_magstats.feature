Feature: Ask for object magnitude statistics

  Scenario Outline: query object magnitude statistics
    Given object ALERCE1 is in the database with magstats for fid 1,2
    And object ALERCE2 is in the database with magstats for fid 1,3
    When request magstats for <object>
    Then retrieve magstats with fid <fid>
    Examples:
      | object  | fid |
      | ALERCE1 | 1,2 |
      | ALERCE2 | 1,3 |

  Scenario: query non-existent object magnitude statistics
    Given object ALERCE1 is in the database with magstats for fid 1,2
    And object ALERCE2 is in the database with magstats for fid 1,3
    When request magstats for ALERCE99
    Then retrieve error code 404

