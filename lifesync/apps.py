# from django.apps import AppConfig


# class LifesyncConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'lifesync'

#     def ready(self):
#         import lifesync.signals


from django.apps import AppConfig

class LifesyncConfig(AppConfig):
    name = 'lifesync'

    def ready(self):
        import lifesync.signals  # noqa
