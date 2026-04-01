from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper


class DatabaseWrapper(SQLiteDatabaseWrapper):
    def get_new_connection(self, conn_params):
        connection = super().get_new_connection(conn_params)
        connection.execute('PRAGMA journal_mode=MEMORY;')
        connection.execute('PRAGMA synchronous=NORMAL;')
        return connection
