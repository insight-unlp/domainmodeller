package ie.deri.unlp.javaservices.topicextraction.filter;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;
import ie.deri.unlp.javaservices.topicextraction.Config;

import java.util.List;

public class AllFilters implements ExtractedTopicsFilter {
    //private static Logger log = Logger.getLogger(AllFilters.class);

    public List<ExtractedTopic> filter(List<ExtractedTopic> extracted) {
    	if (Config.maxTopicsPerDocument != null) {
    		extracted = new MaxExtractedTopicsFilter(Config.maxTopicsPerDocument).filter(extracted);
    	}
        extracted = new ProperExtractedTopicFilter().filter(extracted);
        extracted = new TokenCountRangeFilter(Config.minTokens, Config.maxTokens).filter(extracted);
        
        return extracted;
    }
}
