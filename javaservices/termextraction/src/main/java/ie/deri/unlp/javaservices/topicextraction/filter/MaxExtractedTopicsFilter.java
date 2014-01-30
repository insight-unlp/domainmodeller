package ie.deri.unlp.javaservices.topicextraction.filter;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class MaxExtractedTopicsFilter implements ExtractedTopicsFilter {
    private Integer maxTopics;

    public MaxExtractedTopicsFilter(Integer maxTopics) {
        this.maxTopics = maxTopics;
    }

    @Override
    public List<ExtractedTopic> filter(List<ExtractedTopic> extractedTopics) {
        List<ExtractedTopic> filtered = new ArrayList<ExtractedTopic>();

        Integer size = maxTopics;
        if (size != null) {
            // Sort the list (by offset) to take only the first N topics
            Collections.sort(filtered);
            for(int i=0; i < Math.min(extractedTopics.size(), size); i++) {
                filtered.add(extractedTopics.get(i));
            }
            return filtered;
        }

        return extractedTopics;
    }
}
