Feature: Ask for astro object(s)

  Scenario: query for limits in ndet and firstmjd
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.1      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.2      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request limit values
    Then retrieve min_ndet with value 1
    And retrieve max_ndet with value 7
    And retrieve min_firstmjd with value 1.1
    And retrieve max_firstmjd with value 5.2

  Scenario: get single object
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.1      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.2      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request object with AID ALERCE2
    Then ensure aid is ALERCE2
    And ensure oid is ZTF1,ATLAS2
    And ensure xmatch is present
    And ensure magstats is present
    And ensure features is present
    And ensure probabilities is present

  Scenario: get non existent object
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.1      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.2      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request object with AID ALERCE99
    Then retrieve error code 404

  Scenario Outline: query objects by identifier
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with identifiers <oids>
    Then retrieve objects <objects>
    Examples:
      | oids              | objects                 |
      | ZTF1              | ALERCE2,ALERCE1         |
      | ZTF1,ZTF2         | ALERCE2,ALERCE1,ALERCE3 |
      | ZTF1,ATLAS1       | ALERCE2,ALERCE1         |
      | ALERCE1,ATLAS2    | ALERCE2,ALERCE1,ALERCE4 |
      | ALERCE1,ZTF1,ZTF2 | ALERCE2,ALERCE1,ALERCE3 |

  Scenario: query objects by non present identifiers
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with identifiers ALERCE99,ZTF99,ATLAS99
    Then retrieve empty items

  Scenario Outline: query objects by number of detections
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with ndet between <min> and <max>
    Then retrieve objects <objects>
    Examples:
      | min | max | objects                 |
      | 1   | 6   | ALERCE1,ALERCE2,ALERCE4 |
      | 1   | 4   | ALERCE1,ALERCE2         |
      | 2   | 7   | ALERCE1,ALERCE3,ALERCE4 |

  Scenario: query objects outside range of number of detections
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with ndet between 2 and 3
    Then retrieve empty items

  Scenario Outline: query objects by first detection date
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with firstmjd between <min> and <max>
    Then retrieve objects <objects>
    Examples:
      | min | max | objects                 |
      | 1   | 4   | ALERCE1,ALERCE2,ALERCE4 |
      | 1   | 2.5 | ALERCE1,ALERCE2         |
      | 2   | 7   | ALERCE2,ALERCE3,ALERCE4 |

  Scenario: query objects outside range of first detection date
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with firstmjd between 3.5 and 4.5
    Then retrieve empty items

  Scenario Outline: query objects by last detection date
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with lastmjd between <min> and <max>
    Then retrieve objects <objects>
    Examples:
      | min | max | objects                 |
      | 5   | 15  | ALERCE1,ALERCE3,ALERCE4 |
      | 5   | 10  | ALERCE1,ALERCE3         |
      | 1   | 10  | ALERCE1,ALERCE2,ALERCE3 |

  Scenario: query objects outside range of last detection date
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects with lastmjd between 2.5 and 6.5
    Then retrieve empty items

  Scenario Outline: cone search object queries
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.0    | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects within <radius> arcsec of <ra>/<dec>
    Then retrieve objects <objects>
    Examples:
      | radius | ra   | dec   | objects         |
      | 1800.0 | 0.0  | 80.0  | ALERCE1,ALERCE2 |
      | 1799.0 | 0.0  | 80.0  | ALERCE1         |
      | 1800.0 | 45.0 | -80.5 | ALERCE3         |

    Scenario: cone search query in area without objects
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects within 1 arcsec of 0/0
    Then retrieve empty items

  Scenario Outline: sort objects
    Given objects are in the database with following parameters
      | _id     | oid         | ndet | firstmjd | lastmjd | meanra | meandec |
      | ALERCE1 | ZTF1,ATLAS1 | 4    | 1.0      | 7.0     | 0.0    | 80.0    |
      | ALERCE2 | ZTF1,ATLAS2 | 1    | 2.0      | 2.0     | 0.25   | 80.5    |
      | ALERCE3 | ZTF2        | 7    | 5.0      | 8.0     | 45.0   | -80.0   |
      | ALERCE4 | ATLAS2      | 5    | 3.0      | 12.0    | 180.0  | 0.0     |
    When request objects sorted by <parameter> in <direction> order
    Then retrieve objects <objects>, in that order
    Examples:
      | parameter | direction  | objects                         |
      | ndet      | ascending  | ALERCE2,ALERCE1,ALERCE4,ALERCE3 |
      | firstmjd  | ascending  | ALERCE1,ALERCE2,ALERCE4,ALERCE3 |
      | lastmjd   | ascending  | ALERCE2,ALERCE1,ALERCE3,ALERCE4 |
      | ndet      | descending | ALERCE3,ALERCE4,ALERCE1,ALERCE2 |
      | firstmjd  | descending | ALERCE3,ALERCE4,ALERCE2,ALERCE1 |
      | lastmjd   | descending | ALERCE4,ALERCE3,ALERCE1,ALERCE2 |

  Scenario Outline: query objects by ranking
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with ranking <ranking>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | ranking | classes                     | objects                         |
      | 1       | stamp2,stamp1,lc1,lc2       | ALERCE1,ALERCE2,ALERCE1,ALERCE3 |
      | 2       | stamp1,stamp2,lc3,lc3       | ALERCE1,ALERCE2,ALERCE1,ALERCE3 |
      | 3       | lc2,lc1                     | ALERCE1,ALERCE3                 |

  Scenario Outline: query objects by probability
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with probability <probability>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | probability | classes                      | objects                                 |
      | 0.4         | stamp1,stamp2,stamp1,lc1,lc2 | ALERCE1,ALERCE1,ALERCE2,ALERCE1,ALERCE3 |
      | 0.7         | stamp1,lc2                   | ALERCE2,ALERCE3                         |

  Scenario Outline: query objects by classifier version
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with classifier_version <version>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | version | classes                       | objects                                         |
      | 1.1     | stamp1,stamp2,lc2,lc1         | ALERCE1,ALERCE2,ALERCE1,ALERCE3                 |
      | 1.0     | stamp2,stamp1,lc1,lc3,lc2,lc3 | ALERCE1,ALERCE2,ALERCE1,ALERCE1,ALERCE3,ALERCE3 |

  Scenario Outline: query objects by classifier
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with classifier <classifier>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | classifier | classes                       | objects                                         |
      | stamp      | stamp1,stamp2,stamp1,stamp2   | ALERCE1,ALERCE1,ALERCE2,ALERCE2                 |
      | lc         | lc1,lc2,lc3,lc1,lc2,lc3       | ALERCE1,ALERCE1,ALERCE1,ALERCE3,ALERCE3,ALERCE3 |

  Scenario Outline: query objects by class
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
      | lc              | 1.1                | lc1        | 1.0         | 1       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with class <class>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | class  | classes         | objects                 |
      | lc1    | lc1,lc1,lc1     | ALERCE1,ALERCE2,ALERCE3 |
      | lc2    | lc2,lc2         | ALERCE1,ALERCE3         |
      | stamp1 | stamp1,stamp1   | ALERCE1,ALERCE2         |

  Scenario Outline: object sorting by probabilities
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
    When request objects sorted by probability in <direction> order
    Then retrieve classes <classes> for objects <objects>, respectively, in that order
    Examples:
      | direction  | classes            | objects                         |
      | ascending  | lc1,stamp1,lc1,lc2 | ALERCE3,ALERCE1,ALERCE1,ALERCE3 |
      | descending | lc2,lc1,stamp1,lc1 | ALERCE3,ALERCE1,ALERCE1,ALERCE3 |

  Scenario Outline: query objects out of range
    Given object ALERCE1 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.1                | stamp1     | 0.4         | 2       |
      | stamp           | 1.0                | stamp2     | 0.6         | 1       |
      | lc              | 1.0                | lc1        | 0.5         | 1       |
      | lc              | 1.1                | lc2        | 0.2         | 3       |
      | lc              | 1.0                | lc3        | 0.3         | 2       |
    And object ALERCE2 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | stamp           | 1.0                | stamp1     | 0.7         | 1       |
      | stamp           | 1.1                | stamp2     | 0.3         | 2       |
    And object ALERCE3 is in the database with following probabilities
      | classifier_name | classifier_version | class_name | probability | ranking |
      | lc              | 1.1                | lc1        | 0.1         | 3       |
      | lc              | 1.0                | lc2        | 0.7         | 1       |
      | lc              | 1.0                | lc3        | 0.2         | 2       |
    When request objects with <parameter> <value>
    Then retrieve empty items
    Examples:
      | parameter          | value  |
      | classifier         | fake   |
      | ranking            | 0      |
      | probability        | 1.0    |
      | classifier_version | 2.0    |
      | class              | stamp3 |
