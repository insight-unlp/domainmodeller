package ie.deri.unlp.javaservices.topicextraction.filter;

import ie.deri.unlp.gate.topiccollector.ExtractedTopic;
import ie.deri.unlp.javaservices.nlputil.WordUtils;

import java.util.ArrayList;
import java.util.List;

public class TokenCountRangeFilter implements ExtractedTopicsFilter {
    private Integer minTokens;
    private Integer maxTokens;

    public TokenCountRangeFilter(Integer minTokens, Integer maxTokens) {
        this.minTokens = minTokens;
        this.maxTokens = maxTokens;
    }

    @Override
    public List<ExtractedTopic> filter(List<ExtractedTopic> extracted)  {
        List<ExtractedTopic> filtered = new ArrayList<ExtractedTopic>();

        for (ExtractedTopic extractedTopic : extracted) {
            int tokens = WordUtils.computeTokensNo(extractedTopic.getPattern());
            if (tokens >= minTokens && tokens <= maxTokens) {
                filtered.add(extractedTopic);
            }
        }

        return filtered;
    }
}
