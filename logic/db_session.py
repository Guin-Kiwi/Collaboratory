from database import db_conn 

def get_session(): 
    return db_conn.get_session() 