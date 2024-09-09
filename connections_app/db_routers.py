# db_routers.py

class AdminRouter:
    def db_for_read(self, model, **hints):
        """
        Attempts to read models go to the appropriate database.
        """
        request = hints.get('request')
        if request:
            user = getattr(request, 'user', None)
            if user:
                if not user.is_superuser:
                    return 'restricted_user'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write models go to the appropriate database.
        """
        request = hints.get('request')
        if request:
            user = getattr(request, 'user', None)
            if user:
                if not user.is_superuser:
                    return 'restricted_user'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both models are in the same database.
        """
        if hasattr(obj1, '_state') and hasattr(obj2, '_state'):
            if obj1._state.db == obj2._state.db:
                return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations only on the 'admin' database.
        """
        return db == 'default'