Feature: Ask for astro object data

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
    When request objects with ranking <ranking> and classifier <classifier>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | ranking | classifier | classes                     | objects                         |
      | 1       | lc         | lc1,lc2                     | ALERCE1,ALERCE3                 |
      | 1       | stamp      | stamp2,stamp1               | ALERCE1,ALERCE2                 |
      | 1       | all        | stamp2,lc1,stamp1,lc2       | ALERCE1,ALERCE1,ALERCE2,ALERCE3 |
      | all     | stamp      | stamp1,stamp2,stamp1,stamp2 | ALERCE1,ALERCE1,ALERCE2,ALERCE2 |

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
    When request objects with probability <probability> and classifier <classifier>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | probability | classifier | classes                      | objects                                 |
      | 0.4         | lc         | lc1,lc2                      | ALERCE1,ALERCE3                         |
      | 0.4         | stamp      | stamp1,stamp2,stamp1         | ALERCE1,ALERCE1,ALERCE2                 |
      | 0.4         | all        | stamp1,stamp2,lc1,stamp1,lc2 | ALERCE1,ALERCE1,ALERCE1,ALERCE2,ALERCE3 |

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
    When request objects with classifier_version <version> and classifier <classifier>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | version | classifier | classes         | objects                         |
      | 1.1     | lc         | lc2,lc1         | ALERCE1,ALERCE3                 |
      | 1.0     | lc         | lc1,lc3,lc2,lc3 | ALERCE1,ALERCE1,ALERCE3,ALERCE3 |
      | 1.0     | stamp      | stamp2,stamp1   | ALERCE1,ALERCE2                 |
      | 1.1     | stamp      | stamp1,stamp2   | ALERCE1,ALERCE2                 |

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
    When request objects with class <class> and classifier <classifier>
    Then retrieve classes <classes> for objects <objects>, respectively
    Examples:
      | class  | classifier | classes         | objects                 |
      | lc1    | lc         | lc1,lc1,lc1     | ALERCE1,ALERCE2,ALERCE3 |
      | lc2    | lc         | lc2,lc2         | ALERCE1,ALERCE3         |
      | stamp1 | stamp      | stamp1,stamp1   | ALERCE1,ALERCE2         |

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
    When request objects with <parameter> <value> and classifier <classifier>
    Then retrieve empty items
    Examples:
      | parameter          | value  | classifier  |
      | ranking            | all    | lc_periodic |
      | ranking            | 0      | all         |
      | probability        | 1.0    | all         |
      | classifier_version | 2.0    | all         |
      | class              | stamp3 | stamp       |
