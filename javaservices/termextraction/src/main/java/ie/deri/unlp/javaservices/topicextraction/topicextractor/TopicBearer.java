package ie.deri.unlp.javaservices.topicextraction.topicextractor;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;

import java.util.List;

public class TopicBearer {
    private List<ExtractedTopic> extractedTopics;
    private Integer tokensNumber = 0;

    public void setTokensNumber(Integer tokensNumber) {
        this.tokensNumber = tokensNumber;
    }

    public Integer getTokensNumber() {
        return tokensNumber;
    }

    public void setExtractedTopics(List<ExtractedTopic> extractedTopics) {
        this.extractedTopics = extractedTopics;
    }

    public List<ExtractedTopic> getExtractedTopics() {
        return extractedTopics;
    }
}
