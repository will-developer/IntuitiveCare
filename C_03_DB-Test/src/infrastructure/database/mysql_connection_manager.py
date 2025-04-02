import logging
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

class MySQLConnectionManager:
    """Manages a pool of MySQL database connections for efficient reuse."""
    
    def __init__(self, db_config: dict, pool_size: int = 2):
        """Initialize connection pool with given configuration.
        """
        self._config = db_config
        self._pool = None  # Will hold the connection pool
        
        try:
            # Prepare pool configuration with defaults
            pool_config = self._config.copy()
            pool_config['pool_name'] = pool_config.get('pool_name', 'mypool')
            pool_config['pool_size'] = pool_size
            
            # Create the connection pool
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"MySQL pool '{pool_config['pool_name']}' created (size: {pool_size})")
            
            # Test the pool by getting and immediately releasing a connection
            conn = self.get_connection()
            conn.close()
            logger.info("Connection pool test successful.")
            
        except Error as e:
            logger.error(f"Failed to create connection pool: {e}")
            
            # Handle specific error cases
            if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                logger.error(f"Database '{self._config.get('database')}' doesn't exist")
            elif e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Authentication failed - check credentials")
            elif 'allow_local_infile' in str(e):
                logger.error("LOAD DATA LOCAL INFILE not enabled on server/client")
                
            self._pool = None
            raise  # Re-raise for caller to handle

    def get_connection(self) -> mysql.connector.connection.MySQLConnection:
        """Get a connection from the pool.
        """
        if not self._pool:
            logger.error("Connection pool not available")
            raise ConnectionError("MySQL connection pool not initialized")
            
        try:
            conn = self._pool.get_connection()
            logger.debug("Acquired connection from pool")
            return conn
        except Error as e:
            logger.error(f"Failed to get connection: {e}")
            raise ConnectionError(f"Connection pool error: {e}") from e

    def close_pool(self):
        logger.warning("Closing connection pool (not normally required)")
        # Note: The pool will automatically clean up when garbage collected