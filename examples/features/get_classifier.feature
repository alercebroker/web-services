Feature: Ask for classifiers

  Scenario: query all classifiers
    Given following classifiers are in database
      | classifier_name | classifier_version | classes              |
      | stamp           | 1.0                | stamp1,stamp2,stamp3 |
      | stamp           | 1.1                | stamp1,stamp2        |
      | lc              | 1.0                | lc1,lc2,lc3,lc4      |
    When request all classifiers
    Then retrieve following classifiers
      | classifier_name | classifier_version | classes              |
      | stamp           | 1.0                | stamp1,stamp2,stamp3 |
      | stamp           | 1.1                | stamp1,stamp2        |
      | lc              | 1.0                | lc1,lc2,lc3,lc4      |

  Scenario Outline: query classes by classifier and version
    Given following classifiers are in database
      | classifier_name | classifier_version | classes              |
      | stamp           | 1.0                | stamp1,stamp2,stamp3 |
      | stamp           | 1.1                | stamp1,stamp2        |
      | lc              | 1.0                | lc1,lc2,lc3,lc4      |
    When request classes for classifier <classifier_name> and version <classifier_version>
    Then retrieve classes with names <classes>
    Examples:
      | classifier_name | classifier_version | classes              |
      | stamp           | 1.0                | stamp1,stamp2,stamp3 |
      | stamp           | 1.1                | stamp1,stamp2        |
      | lc              | 1.0                | lc1,lc2,lc3,lc4      |

  Scenario Outline: query classes by non-existent classifier/version
    Given following classifiers are in database
      | classifier_name | classifier_version | classes              |
      | stamp           | 1.0                | stamp1,stamp2,stamp3 |
      | stamp           | 1.1                | stamp1,stamp2        |
      | lc              | 1.0                | lc1,lc2,lc3,lc4      |
    When request classes for classifier <classifier_name> and version <classifier_version>
    Then retrieve error code 404
    Examples:
      | classifier_name | classifier_version |
      | stamp           | 2.0                |
      | fake            | 1.0                |
