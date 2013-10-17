from settingsapp.models import Setting


def get_setting(name, default):
    """
    TODO encrypt using secret
    """
    try:
        setting = Setting.query.get(name)
        return setting.value_decrypted
    except AttributeError:
        return default
