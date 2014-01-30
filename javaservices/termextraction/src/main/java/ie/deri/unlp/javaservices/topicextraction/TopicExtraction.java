package ie.deri.unlp.javaservices.topicextraction;

import gate.util.GateException;
import ie.deri.unlp.gate.topiccollector.ExtractedTopic;
import ie.deri.unlp.javaservices.textextraction.DocumentConversionException;
import ie.deri.unlp.javaservices.textextraction.TextExtractor;
import ie.deri.unlp.javaservices.topicextraction.data.DomainModel;
import ie.deri.unlp.javaservices.topicextraction.data.Topic;
import ie.deri.unlp.javaservices.topicextraction.data.TopicAdapter;
import ie.deri.unlp.javaservices.topicextraction.filter.AllFilters;
import ie.deri.unlp.javaservices.topicextraction.filter.ExtractedTopicsFilter;
import ie.deri.unlp.javaservices.topicextraction.topicextractor.TopicBearer;
import ie.deri.unlp.javaservices.topicextraction.topicextractor.TopicExtractor;
import ie.deri.unlp.javaservices.topicextraction.topicextractor.gate.TopicExtractorGate;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Set;

/**
 * Ties everything together (extraction, filtering, indexing, data adaptors)
 * See project README.txt for diagram
 */
public class TopicExtraction {
    private TopicExtractor topicExtractor;
    //private static Logger logger = Logger.getLogger(TopicExtraction.class);
    private ExtractedTopicsFilter extractedTopicsFilter;
    
    public TopicExtraction() throws GateException {
        topicExtractor = TopicExtractorGate.getInstance();
        extractedTopicsFilter = new AllFilters();
    }
    
    public TopicExtraction(TopicExtractor topicExtractor, ExtractedTopicsFilter extractedTopicsFilter) {
		this.topicExtractor = topicExtractor;
		this.extractedTopicsFilter = extractedTopicsFilter;
	}
    
	private void filterTopics(TopicBearer tb) {
        //Filter topics
        List<ExtractedTopic> extractedTopicList = tb.getExtractedTopics();
        if (extractedTopicList != null) {
            List<ExtractedTopic> filtered = extractedTopicsFilter.filter(extractedTopicList);
            tb.setExtractedTopics(filtered);
        }
    }

    public Set<Topic> extractTopics(String text, DomainModel domainModel) 
    		throws GateException, IOException {
        TopicBearer tb = topicExtractor.extractTopics(text, domainModel);
        filterTopics(tb);
        
        TopicAdapter topicAdapter = new TopicAdapter(tb.getExtractedTopics(), text);
        Set<Topic> topics = topicAdapter.convertExtractedTopics();
        return topics; 
    }

    public Set<Topic> extractTopics(File f, DomainModel domainModel) 
    		throws GateException, IOException, DocumentConversionException {
    	return extractTopics(TextExtractor.extractText(f), domainModel);
    }
    
    public Set<Topic> extractTopics(InputStream is, String mimeType, DomainModel domainModel) 
    		throws GateException, IOException, DocumentConversionException {
    	return extractTopics(TextExtractor.extractText(is, mimeType), domainModel);
    }
}


