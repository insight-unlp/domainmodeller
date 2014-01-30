package ie.deri.unlp.javaservices.topicextraction.filter;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;
import ie.deri.unlp.javaservices.nlputil.FilterUtils;

import java.util.ArrayList;
import java.util.List;

import org.apache.log4j.Logger;

public class ProperExtractedTopicFilter implements ExtractedTopicsFilter {
	private static Logger logger = Logger.getLogger(ProperExtractedTopicFilter.class);
	
    @Override
    public List<ExtractedTopic> filter(List<ExtractedTopic> extracted) {
        List<ExtractedTopic> filtered = new ArrayList<ExtractedTopic>();

        for (ExtractedTopic extractedTopic : extracted) {
            if (FilterUtils.isProperTopic(extractedTopic.getTopicString())) {
                filtered.add(extractedTopic);
                logger.debug("PROPER TOPIC: rootSequence=" + extractedTopic.getRootSequence()
                		+ "; topicString="+extractedTopic.getTopicString());
            } else {
            	logger.info("NOT A PROPER TOPIC: rootSequence=" + extractedTopic.getRootSequence()
            			+ "; topicString="+extractedTopic.getTopicString());
            }
            
        }

        return filtered;
    }
}
