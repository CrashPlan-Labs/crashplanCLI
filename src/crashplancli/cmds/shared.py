from functools import lru_cache

from crashplancli.errors import UserDoesNotExistError


@lru_cache(maxsize=None)
def get_user_id(sdk, username):
    """Returns the user's UID.
    Raises `UserDoesNotExistError` if the user doesn't exist in the crashplan server.

    Args:
        sdk (pycpg.sdk.SDKClient): The pycpg sdk.
        username (str or unicode): The username of the user to get an ID for.

    Returns:
         str: The user ID for the user with the given username.
    """
    users = sdk.users.get_by_username(username)["users"]
    if not users:
        raise UserDoesNotExistError(username)
    return users[0]["userUid"]
