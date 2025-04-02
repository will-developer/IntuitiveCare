import pytest
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

print("\nAttempting to load test environment variables...") # Log attempt
dotenv_path = Path(__file__).resolve().parent.parent / '.env.test'
if dotenv_path.exists():
    print(f"Loading test environment variables from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, override=True) # Override existing vars
else:
    print(".env.test not found, attempting to load from .env or use system variables.")
    # Ensure .env is loaded if .env.test doesn't exist
    dotenv_path_main = Path(__file__).resolve().parent.parent / '.env'
    if dotenv_path_main.exists():
        print(f"Loading environment variables from: {dotenv_path_main}")
        load_dotenv(dotenv_path=dotenv_path_main)
    else:
        print(".env also not found. Relying on system environment variables.")

# Configure basic logging for tests if needed (can be overridden by pytest config)
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'WARNING').upper(),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

requires_db = pytest.mark.skipif(
    not all(os.getenv(k) for k in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']),
    reason="Database environment variables not fully configured for testing (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)"
)


@pytest.fixture(scope="session")
def test_db_config():
    """Provides database configuration dictionary for tests."""
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'allow_local_infile': True,
        # Use a smaller pool for tests if desired, or connect directly
        'pool_name': os.getenv('DB_POOL_NAME', 'pytest_pool'),
        'pool_size': int(os.getenv('DB_POOL_SIZE', 1))
    }
    # Check required fields specifically
    required_keys = ['host', 'user', 'password', 'database']
    if not all(config.get(k) for k in required_keys):
         pytest.skip(f"Database test configuration is incomplete. Missing: {[k for k in required_keys if not config.get(k)]}")
    logger.info(f"Test DB Config loaded: Host={config['host']}, DB={config['database']}, User={config['user']}")
    return config

@pytest.fixture(scope="function") # Function scope for clean state per test
def db_connection(test_db_config):
    """Yields a direct database connection for test setup/teardown."""
    conn = None
    logger.debug(f"Attempting to connect to test database: {test_db_config['database']} on {test_db_config['host']}")
    try:
        # Connect directly without pooling for setup/teardown simplicity
        conn = mysql.connector.connect(
            host=test_db_config['host'],
            port=test_db_config['port'],
            user=test_db_config['user'],
            password=test_db_config['password'],
            database=test_db_config['database'],
            autocommit=True # Make setup/teardown easier
        )
        logger.info(f"Connected to test database: {test_db_config['database']}")
        yield conn
    except Error as e:
        logger.error(f"Failed to connect to test database: {e}")
        pytest.fail(f"Failed to connect to test database: {e}")
    finally:
        if conn and conn.is_connected():
            logger.info("Closing test database connection.")
            conn.close()


@pytest.fixture(scope="function", autouse=True) # Run automatically for each test function using db_connection
def setup_test_database(request):
    """Cleans the database tables before each test function marked with 'database'."""
    # Only run this fixture if the test function requires db_connection implicitly or explicitly
    # and is marked with 'database'
    if "db_connection" in request.fixturenames and request.node.get_closest_marker("database"):
        db_conn = request.getfixturevalue("db_connection") # Get the actual connection
        cursor = None
        logger.info("Setting up test database (clearing tables)...")
        try:
            cursor = db_conn.cursor()
            # Disable FK checks
            logger.debug("Disabling foreign key checks.")
            cursor.execute("SET SESSION foreign_key_checks = 0;")
            # Truncate tables (order might matter if DELETE was used instead of TRUNCATE)
            logger.debug("Truncating 'accounting' table...")
            cursor.execute("TRUNCATE TABLE accounting;")
            logger.debug("Truncating 'operators' table...")
            cursor.execute("TRUNCATE TABLE operators;")
            # Re-enable FK checks
            logger.debug("Re-enabling foreign key checks.")
            cursor.execute("SET SESSION foreign_key_checks = 1;")
            db_conn.commit() # Ensure changes are committed
            logger.info("Test database tables cleared.")
            yield # Let the test run
            logger.info("Test function finished.") # Optional: add teardown actions here if needed

        except Error as e:
            logger.error(f"Failed during test database setup: {e}")
            # If setup fails, skip the test
            pytest.fail(f"Failed during test database setup: {e}")
        finally:
            if cursor:
                cursor.close()
            # Connection is closed by db_connection fixture
    else:
        # If the test doesn't need the DB or isn't marked, just yield
        yield


# --- Filesystem Fixture ---
@pytest.fixture
def temp_data_dir(tmp_path):
    """Creates a temporary data directory structure similar to the project."""
    base = tmp_path / "data"
    dirs = {
        "base": base,
        "accounting": base / "accounting",
        "zips": base / "accounting" / "zips",
        "csvs": base / "accounting" / "csvs",
        "operators": base / "operators",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    # Add paths for specific files used in tests
    dirs["operators_csv"] = dirs["operators"] / "operators.csv"
    logger.debug(f"Created temporary data directory structure at {base}")
    return dirs