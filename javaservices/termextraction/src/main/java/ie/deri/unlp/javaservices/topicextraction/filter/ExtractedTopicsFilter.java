package ie.deri.unlp.javaservices.topicextraction.filter;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;

import java.util.List;

public interface ExtractedTopicsFilter {
    public List<ExtractedTopic> filter(List<ExtractedTopic> extracted);
}