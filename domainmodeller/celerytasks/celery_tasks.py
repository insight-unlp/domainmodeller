from celery.utils.log import get_task_logger
from domainmodeller.termextraction.JavaServicesTermExtractor import JavaServicesTermExtractor
from celery.app.base import Celery

from domainmodeller import settings
import domainmodeller.celeryconfig

logger = get_task_logger(__name__)

celery = Celery()
celery.config_from_object(domainmodeller.celeryconfig)


term_extractor = JavaServicesTermExtractor(settings.JAVA_SERVICES)
@celery.task    
def extract_terms(raw_text, domain_model):
    terms = term_extractor.extract_terms(raw_text, domain_model)
    return terms
