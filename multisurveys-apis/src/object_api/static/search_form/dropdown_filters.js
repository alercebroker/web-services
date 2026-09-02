

export class Dropdown {

    constructor(classifiers) {
        this._classifiers = classifiers;
        this._filtered_classifiers = [];
        this._priorities_by_survey = {}
    }

    get priorities_by_survey() {
        return this._priorities_by_survey;
    }

    get filtered_classifiers() {
        return this._filtered_classifiers;
    }


    set priorities_by_survey(survey_id) {
        if (survey_id === "ztf") {
            this._priorities_by_survey = {
                5: 0,
                4: 1,
                2: 2,
            };
        }
        else if (survey_id === "lsst") {
            this._priorities_by_survey = {
                3: 0,
                1: 1,
            };
        } else {
            this._priorities_by_survey = {};
        }

    }


    filter_classifiers_by_survey(survey_id) {
        this._filtered_classifiers = this._classifiers.filter(classifier => classifier.survey_id === survey_id);
    }

    order_by_priority(empty_array) {
        this._filtered_classifiers.forEach(classifier => {
            if (classifier.classifier_id in this._priorities_by_survey) {
                let index = this._priorities_by_survey[classifier.classifier_id];
                empty_array[index] = classifier;
            }
        });

        this._filtered_classifiers = [...empty_array.flat()]
    }


}
