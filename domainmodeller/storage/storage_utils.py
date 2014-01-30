'''SQLAlchemy utilities'''

from domainmodeller.storage.schema import schema_classes, Topic, get_primary_keys, get_foreign_keys_to,\
    Base
from sqlalchemy.sql.expression import func

def remove_filtered_topics(s):
    '''After performing topic filtering, filtered topics should be removed from the
    database. Otherwise we have to take care to always query doing Topic.filtered==false,
    which is very error prone.
    
    Note: Previously we used mirror tables to store filtered topics, but because
    of all of the foreign key constraints, this became unmaintainable.
    
    TODO: Dump the filtered data to a .sql file so filtering can be undone.
    TODO: Very very slow in InnoDB, due to log file writing, do it in chunks.
          http://mysql.rjweb.org/doc.php/deletebig#innodb_and_undo
    '''

    q_filtered_t = s.query(Topic.id).filter(Topic.filtered == True)

    # Delete foreign keys
    for fk_class, fk in get_foreign_keys_to(Topic.id):
        q = s.query(fk_class).filter(fk.in_(q_filtered_t.subquery()))
        q.delete(synchronize_session=False)

    q_filtered_t.delete(synchronize_session=False)
    
def count_all_tables(session):
    for clazz in sorted(schema_classes):
        primary_key = get_primary_keys(clazz)[0]
        # func.count is much faster on MySQL than .count()
        count_q = session.query(func.count(primary_key))
        yield clazz, count_q.scalar()

def reset_tables(s, *classes):
    '''Drop and recreates a set of tables. Workaround for InnoDBs TRUNCATE limitations and 
    awful awful slowness with DELETE FROM.
    
    Warning: Only use if there are no cascades from deleted etc.'''

    engine = s.bind
    for clazz in classes:
        clazz.__table__.drop(engine)
    

    meta = Base.metadata  # @UndefinedVariable    
    meta.create_all(engine, checkfirst=True)

def bulk_insert(s, schema_class, dict_objects):
    '''Bulk insert dictionary objects (using the SQLAlchemy Core instead of the ORM).
    Can have huge speed increases and memory reductions. The ORM can not do this
    because it has to keep track of the primary keys of the object, so it does individual
    insert statements.'''
    table = schema_class.__table__
    s.execute(table.insert(), dict_objects)
