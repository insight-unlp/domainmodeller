DATABASE='testing'

SOLR_ROOT = 'http://localhost:8080/solr/'

BACKEND = {
    'backend': 'mysql',
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'debug': False
}

JAVA_SERVICES = 'http://localhost:8082'

# Solr URLs for ngram filtering/dbpedia title lookup
DBPEDIA_LOOKUP_SERVICE = 'http://localhost:8983/solr/dbpedialookup'

# If set to True, configure Hadoop paths in client.cfg. See Luigi docs for details.
LUIGI_USE_HADOOP=False
