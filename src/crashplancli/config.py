import os
from configparser import ConfigParser

import crashplancli.util as util


class NoConfigProfileError(Exception):
    def __init__(self, profile_arg_name=None):
        message = (
            f"Profile '{profile_arg_name}' does not exist."
            if profile_arg_name
            else "Profile does not exist."
        )
        super().__init__(message)


class ConfigAccessor:
    DEFAULT_VALUE = "__DEFAULT__"
    AUTHORITY_KEY = "cpg_authority_url"
    USERNAME_KEY = "cpg_username"
    IGNORE_SSL_ERRORS_KEY = "ignore-ssl-errors"
    API_CLIENT_AUTH_KEY = "api-client-auth"
    DEFAULT_PROFILE = "default_profile"
    _INTERNAL_SECTION = "Internal"

    def __init__(self, parser):
        self.parser = parser
        file_name = "config.cfg"
        self.path = os.path.join(util.get_user_project_path(), file_name)
        if not os.path.exists(self.path):
            self._create_internal_section()
            self._save()
        else:
            self.parser.read(self.path)

    def get_profile(self, name=None):
        """Returns the profile with the given name.
        If name is None, returns the default profile.
        If the name does not exist or there is no existing profile, it will throw an exception.
        """
        name = name or self._default_profile_name
        if name not in self.parser.sections() or name == self.DEFAULT_VALUE:
            name = name if name != self.DEFAULT_VALUE else None
            raise NoConfigProfileError(name)
        return self.parser[name]

    def get_all_profiles(self):
        """Returns all the available profiles."""
        profiles = []
        names = self._get_profile_names()
        for name in names:
            profiles.append(self.get_profile(name))
        return profiles

    def create_profile(
        self,
        name,
        server,
        username,
        ignore_ssl_errors,
        api_client_auth,
    ):
        """Creates a new profile if one does not already exist for that name."""
        try:
            self.get_profile(name)
        except NoConfigProfileError as ex:
            if name is not None and name != self.DEFAULT_VALUE:
                self._create_profile_section(name)
            else:
                raise ex

        profile = self.get_profile(name)
        self.update_profile(
            profile.name,
            server,
            username,
            ignore_ssl_errors,
            api_client_auth,
        )
        self._try_complete_setup(profile)

    def update_profile(
        self,
        name,
        server=None,
        username=None,
        ignore_ssl_errors=None,
        api_client_auth=None,
    ):
        profile = self.get_profile(name)
        if server:
            profile[self.AUTHORITY_KEY] = server.strip()
        if username:
            profile[self.USERNAME_KEY] = username.strip()
        if ignore_ssl_errors is not None:
            profile[self.IGNORE_SSL_ERRORS_KEY] = str(ignore_ssl_errors)
        if api_client_auth is not None:
            profile[self.API_CLIENT_AUTH_KEY] = str(api_client_auth)
        self._save()

    def switch_default_profile(self, new_default_name):
        """Changes what is marked as the default profile in the internal section."""
        if self.get_profile(new_default_name) is None:
            raise NoConfigProfileError(new_default_name)
        self._internal[self.DEFAULT_PROFILE] = new_default_name
        self._save()

    def delete_profile(self, name):
        """Deletes a profile."""
        if self.get_profile(name) is None:
            raise NoConfigProfileError(name)
        self.parser.remove_section(name)
        if name == self._default_profile_name:
            self._internal[self.DEFAULT_PROFILE] = self.DEFAULT_VALUE
        self._save()

    @property
    def _internal(self):
        return self.parser[self._INTERNAL_SECTION]

    @property
    def _default_profile_name(self):
        return self._internal[self.DEFAULT_PROFILE]

    def _get_profile_names(self):
        names = list(self.parser.sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def _create_internal_section(self):
        self.parser.add_section(self._INTERNAL_SECTION)
        self.parser[self._INTERNAL_SECTION] = {}
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_PROFILE] = self.DEFAULT_VALUE

    def _create_profile_section(self, name):
        self.parser.add_section(name)
        self.parser[name] = {}
        self.parser[name][self.AUTHORITY_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.USERNAME_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.IGNORE_SSL_ERRORS_KEY] = str(False)
        self.parser[name][self.API_CLIENT_AUTH_KEY] = str(False)

    def _save(self):
        with open(self.path, "w+", encoding="utf-8") as file:
            self.parser.write(file)

    def _try_complete_setup(self, profile):
        authority = profile.get(self.AUTHORITY_KEY)
        username = profile.get(self.USERNAME_KEY)

        authority_valid = authority and authority != self.DEFAULT_VALUE
        username_valid = username and username != self.DEFAULT_VALUE

        if not authority_valid or not username_valid:
            return

        self._save()

        default_profile = self._internal.get(self.DEFAULT_PROFILE)
        if default_profile is None or default_profile == self.DEFAULT_VALUE:
            self.switch_default_profile(profile.name)


config_accessor = ConfigAccessor(ConfigParser())
