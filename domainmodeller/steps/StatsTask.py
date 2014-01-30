from .IStep import IStep
from domainmodeller.storage.schema import Paper, Topic
import sys
from domainmodeller.storage import storage_utils
from sqlalchemy.sql.expression import func

class StatsTask(IStep):
    
    def run(self, s, writer=sys.stdout):
        flag_ok = Paper.flag_term_extraction_ok
        flag_failed = Paper.flag_text_extraction_failed
        ok = s.query(func.count(Paper.id)).filter(flag_ok==True).scalar()
        not_attempted = s.query(func.count(Paper.id))\
                        .filter(flag_ok==False, flag_failed==False).scalar()        
        writer.write('Term extraction: Ok %d, Not attempted: %d\n' % 
                         (ok, not_attempted))
        
        match = s.query(func.count(Topic.id)).filter(Topic.dbpedia_url!=None).scalar()
        attempt = s.query(func.count(Topic.id))\
                    .filter(Topic.flag_dbpedia_lookup_attempted).scalar()
        writer.write('DBPedia lookup: Matched %d topics, attempted %d topics\n' % 
                         (match, attempt))

        writer.write('\nTable counts:\n')
        for clazz, count in storage_utils.count_all_tables(s):
            writer.write("%8d %s\n" % (count, clazz.__name__))
