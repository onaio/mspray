"""
apps module for reveal app
"""
from django.apps import AppConfig


class RevealConfig(AppConfig):
    """
    reveal app config class
    """

    name = 'reveal'
    app_label = 'reveal'

    def ready(self):
        """
        Do stuff when the app is ready
        """
        # set up app settings
        from django.conf import settings  # noqa
        import mspray.apps.reveal.settings as defaults  # noqa

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
