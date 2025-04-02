# src/infrastructure/database/mysql_connection_manager.py
import logging
import mysql.connector
from mysql.connector import pooling, Error

logger = logging.getLogger(__name__)

class MySQLConnectionManager:
    def __init__(self, db_config: dict, pool_size: int = 2):
        self._config = db_config
        self._pool = None
        try:
            pool_config = self._config.copy()
            pool_config['pool_name'] = pool_config.get('pool_name', 'mypool')
            pool_config['pool_size'] = pool_size
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"MySQL connection pool '{pool_config['pool_name']}' created with size {pool_size}")
            conn = self.get_connection()
            conn.close()
            logger.info("Database connection pool test successful.")
        except Error as e:
            logger.error(f"Failed to create MySQL connection pool: {e}")
            if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                logger.error(f"Database '{self._config.get('database')}' does not exist.")
            elif e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Access denied. Check username and password.")
            elif 'allow_local_infile' in str(e):
                 logger.error("Error: LOAD DATA LOCAL INFILE probably not enabled on server or client connection.")
            self._pool = None
            raise

    def get_connection(self):
        if not self._pool:
            logger.error("Connection pool is not available.")
            raise ConnectionError("MySQL connection pool not initialized.")
        try:
            conn = self._pool.get_connection()
            logger.debug("Acquired connection from pool.")
            return conn
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise ConnectionError(f"Failed to get connection from pool: {e}") from e

    def close_pool(self):
        logger.warning("Closing connection pool - not typically required.")