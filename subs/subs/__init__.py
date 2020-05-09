import logging
from contextlib import contextmanager

from . import config
import records

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class ADatabase(records.Database):
    @contextmanager
    def transaction(self):
        """A context manager for executing a transaction on this Database."""

        conn = self.get_connection()
        tx = conn.transaction()
        try:
            yield conn
            tx.commit()
        except Exception as e:
            tx.rollback()
            raise e
        finally:
            conn.close()


db: records.Database = ADatabase(config.DB_URL)
