"""Reactive IRS App config"""
from django.apps import AppConfig


class IRSConfig(AppConfig):
    """
    Reactive IRS app config class
    """

    name = "mspray.apps.reactive.irs"
    app_label = "reactive_irs"

    def ready(self):
        """
        Do stuff when the app is ready
        """
        # pylint: disable=unused-variable
        import mspray.apps.reactive.irs.signals  # noqa

        # set up app settings
        from django.conf import settings  # noqa
        import mspray.apps.reactive.irs.settings as defaults  # noqa

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
