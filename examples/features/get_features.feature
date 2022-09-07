Feature: Ask for features

  Scenario: query all features for object
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request all features for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |

  Scenario: query all features for non-existent object
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request all features for ALERCE99
    Then retrieve error code 404

  Scenario: query all features given fid
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request features with fid 1 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |

  Scenario: query all features given non-existent fid
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request features with fid 3 for ALERCE1
    Then retrieve empty features

  Scenario: query all features given version
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request features with version 1.0 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |

  Scenario: query all features given non-existent version
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request features with version 2.0 for ALERCE1
    Then retrieve empty features

  Scenario: query all features given fid and version
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request features with fid 1 and version 1.0 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |

  Scenario: query features by name for object
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |

  Scenario: query features by non-existent name for object
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request feature f99 for ALERCE1
    Then retrieve empty features

  Scenario: query features by non-existent name for non-existent object
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
    When request feature f99 for ALERCE99
    Then retrieve error code 404

  Scenario: query features by name given fid
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 with fid 1 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |

  Scenario: query features by name given non-existent fid
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 with fid 3 for ALERCE1
    Then retrieve empty features

  Scenario: query features by name given version
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 with version 1.0 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 1.0   | 2   | 1.0     |

  Scenario: query features by name given non-existent fid
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 with version 2.0 for ALERCE1
    Then retrieve empty features

  Scenario: query all features given fid and version
    Given object ALERCE1 is in the database with following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
      | f1   | 0.9   | 1   | 1.1     |
      | f1   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 2   | 1.0     |
      | f2   | 1.0   | 1   | 1.0     |
    When request feature f1 with fid 1 and version 1.0 for ALERCE1
    Then retrieve following features
      | name | value | fid | version |
      | f1   | 1.0   | 1   | 1.0     |
