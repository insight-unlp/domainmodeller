# Use in-memory databases so tests run fast

DATABASE = 'testing'
SOLR_ROOT = 'http://localhost:8080/solr/'

BACKEND = {
    'backend': 'sqlite_memory',
    'debug': False
}