import json
from utils.exceptions import BadSettingException


class RalidatorCoreSettingsFactory(object):
    """The settings parser and validator for the ralidator core.
    It have a variable to configure the accepted settings keys with
    the expected type, an a variable to identify the required settings.

    User filters "*" mean that all the app filters will be applied.
    """

    REQUIERED_SETTINGS = ["SECRET_KEY"]
    SETTINGS_KEYS = {
        "ON_AUTH_ERROR_DEFAULT_USER": bool,
        "USER_API_URL": str,
        "USER_API_TOKEN": str,
        "SECRET_KEY": str,
        "DEFAULT_USER_PERMISSIONS": list,
        "DEFAULT_USER_FILTERS": list,
    }

    def __init__(self) -> None:
        """Constructor Method"""
        self.settings = {
            "ON_AUTH_ERROR_DEFAULT_USER": False,
            "USER_API_URL": None,
            "USER_API_TOKEN": None,
            "DEFAULT_USER_PERMISSIONS": ["basic_user"],
            "DEFAULT_USER_FILTERS": ["*"],
        }
        self.value_settings_error = []
        self.missing_setting_errors = []

    def _add_setting(self, setting_key, setting_value):
        """It adds a setting to the object. It check if its a accepted
        setting, and if the value provided is correct. If the value isn't
        correct an error is stored.

        :param setting_key: The key for the setting to store
        :type setting_key: str
        :param setting_value: The value to stored with the setting_key
        :type setting_value: any
        """
        if setting_key in self.SETTINGS_KEYS:
            if isinstance(
                setting_value,
                self.SETTINGS_KEYS[setting_key]
            ):
                self.settings[setting_key] = setting_value
            else:
                self.value_settings_error.append(
                    {
                        "key": setting_key,
                        "value": setting_value,
                        "expected": RalidatorCoreSettingsFactory.SETTINGS_KEYS[
                            setting_key
                        ],
                    }
                )

    def _check_setting(self):
        """It check if all the required settings are defined, if not,
        an error is stored for each missing key. Finally if check if
        any errors where found in the processing of the setting.

        :return: True if the settings are correct, False if there are
            any errors.
        :rtype: bool
        """
        for sett in self.REQUIERED_SETTINGS:
            if not sett in self.settings:
                self.missing_setting_errors.append(sett)

        if (
            len(self.value_settings_error) == 0
            and len(self.missing_setting_errors) == 0
        ):
            return True
        return False

    def get_errors(self):
        """Parse the erros into error messages, and return a list
        of error messages

        :return: a list with a error message apropiate to each
            error found
        :rtype: list[str]
        """
        error_messages = []
        for err in self.value_settings_error:
            error_messages.append(
                f"Bad balue for {err['key']}. Received: {err['value']} expected {err['expected']}"
            )
        for err in self.missing_setting_errors:
            error_messages.append(f"Missing key: {err}")
        return error_messages

    def get_settings(self) -> dict:
        """Getter for the settings attribute

        :return: a dictionary with the parsed and validated
            settings.
        :rtype: dict
        """
        return self.settings

    @classmethod
    def from_dict(cls, dict_setting: dict):
        """Constructor for settings from a dict variable.

        :param dict_setting: a dictionary where the keys map
            to the spected setting keys.
        :type dict_setting: dict
        :raise: BadSettingException if a setting is missing,
            or it have a bad value
        """
        ralidator_setting = RalidatorCoreSettingsFactory()

        for key in dict_setting:
            ralidator_setting._add_setting(key, dict_setting[key])

        if ralidator_setting._check_setting():
            return ralidator_setting
        else:
            error_msg = ralidator_setting.get_errors()
            raise BadSettingException(error_msg)

    @classmethod
    def from_yml(cls, yml_setting):
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_setting):
        """Constructor for settings from a json string.

        :param dict_setting: json string with the settings
            variables declared
        :type dict_setting: str
        :raise: BadSettingException if a setting is missing,
            or it have a bad value
        """
        j_dict = json.loads(json_setting)
        return cls.from_dict(j_dict)
