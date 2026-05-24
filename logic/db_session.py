from database import db_conn 

def get_session():
    """Return a new database session from the shared connection."""
    return db_conn.get_session()