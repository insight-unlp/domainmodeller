from sqlalchemy.engine import create_engine
from sqlalchemy import event

def init_solr(database, solr_root):
    from domainmodeller.storage.SolrStorage import SolrStorage
    url = solr_root.rstrip('/') + '/' + database
    return SolrStorage(url)

def init_storage(database, backend, user=None, password=None, host=None, debug=False):
    engine = _init_engine(database, backend, user=user, password=password, 
                          host=host, debug=debug)
    from domainmodeller.storage.SQLAlchemyBackend import SQLAlchemyBackend
    return SQLAlchemyBackend(engine)

def _init_engine(database, backend, user=None, password=None, host=None, debug=False):
    if backend=='mysql':
        # Use oursql because other backends do not properly support MySQL cursors,
        # i.e. if you want to stream a large table through memory, other backends
        # will pull every row in the table into memory. The SQLAlchemy docs for yield_per
        # say that only psycopg2 is supported, but OurSQL also streams by default.
        if password:
            url = ('mysql+oursql://%s:%s@%s/%s?charset=utf8&use_unicode=1' % 
                   (user, password, host, database))
        else:
            url = ('mysql+oursql://%s@%s/%s?charset=utf8&use_unicode=1' % 
                   (user, host, database))
        
    elif backend=='sqlite_memory':
        url = 'sqlite:///:memory:'
    else:
        raise ValueError('Unknown database backend %s' % backend)

    engine = create_engine(url, echo=debug)
    
    # Enforce referential integrity on sqlite_memory for more rigorous tests.
    # http://stackoverflow.com/a/7831210/281469
    if backend=='sqlite_memory':
        event.listen(engine, 'connect', _fk_pragma_on_connect)
    return engine



def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')