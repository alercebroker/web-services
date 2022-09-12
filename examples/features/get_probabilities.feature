Feature: Ask for object probabilities

  Scenario Outline: query object full probabilities
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
    When request all probabilities for <object>
    Then retrieve classes <classes> with probabilities <probabilities>
    Examples:
      | object  | classes                   | probabilities       |
      | ALERCE1 | stamp1,stamp2,lc1,lc2,lc3 | 0.4,0.6,0.5,0.2,0.3 |
      | ALERCE2 | stamp1,stamp2             | 0.7,0.3             |
      | ALERCE3 | lc1,lc2,lc3               | 0.1,0.7,0.2         |

  Scenario Outline: query object probabilities for given classifier
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
    When request probabilities for <classifier> classifier for <object>
    Then retrieve classes <classes> with probabilities <probabilities>
    Examples:
      | object  | classifier | classes       | probabilities |
      | ALERCE1 | stamp      | stamp1,stamp2 | 0.4,0.6       |
      | ALERCE2 | stamp      | stamp1,stamp2 | 0.7,0.3       |
      | ALERCE1 | lc         | lc1,lc2,lc3   | 0.5,0.2,0.3   |
      | ALERCE3 | lc         | lc1,lc2,lc3   | 0.1,0.7,0.2   |

  Scenario Outline: query object probabilities for given classifier and version
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
    When request probabilities for <classifier> classifier and version <version> for <object>
    Then retrieve classes <classes> with probabilities <probabilities>
    Examples:
      | object  | classifier | version | classes | probabilities |
      | ALERCE1 | stamp      | 1.0     | stamp2  | 0.6           |
      | ALERCE2 | stamp      | 1.0     | stamp1  | 0.7           |
      | ALERCE1 | lc         | 1.0     | lc1,lc3 | 0.5,0.3       |
      | ALERCE3 | lc         | 1.0     | lc2,lc3 | 0.7,0.2       |
      | ALERCE1 | stamp      | 1.1     | stamp1  | 0.4           |
      | ALERCE2 | stamp      | 1.1     | stamp2  | 0.3           |
      | ALERCE1 | lc         | 1.1     | lc2     | 0.2           |
      | ALERCE3 | lc         | 1.1     | lc1     | 0.1           |

  Scenario Outline: query object probabilities for non-existent classifier/version
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
    When request probabilities for <classifier> classifier and version <version> for <object>
    Then retrieve empty probabilities
    Examples:
      | object  | classifier | version |
      | ALERCE1 | stamp      | 2.0     |
      | ALERCE2 | lc         | 2.0     |
      | ALERCE3 | fake       | 1.0     |

  Scenario: query non-existent object probabilities
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
    When request all probabilities for ALERCE99
    Then retrieve error code 404
