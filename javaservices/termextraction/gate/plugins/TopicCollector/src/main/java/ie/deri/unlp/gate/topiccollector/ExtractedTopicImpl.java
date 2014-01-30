/**
 * 
 */
package ie.deri.unlp.gate.topiccollector;



import ie.deri.unlp.gate.topiccollector.ExtractedTopic;

import java.io.Serializable;
/**
 * Class used to store the information extracted by the gate pipeline about a
 * topic
 * 
 * @author Georgeta Bordea
 */
public class ExtractedTopicImpl implements ExtractedTopic, Serializable {
  private static final long serialVersionUID = 8328237576668814317L;

  private String topicString = null;
  private String context = null;
  private String pattern = null;
  private String contextPattern = null;
  private String rootSequence = null;
  private String acronym = null;
  private String expandedAcronym = null;
  private Long offset = null;

  public ExtractedTopicImpl() {
    super();
  }

  public ExtractedTopicImpl(String topicString, String context, String pattern,
      String contextPattern, String rooSequence, String acronym, String 
      expandedAcronym, Long offset) {
    super();
    this.topicString = topicString;
    this.context = context;
    this.pattern = pattern;
    this.contextPattern = contextPattern;
    this.rootSequence = rooSequence;
    this.acronym = acronym;
    this.expandedAcronym = expandedAcronym;
    this.offset = offset;
  }

  public String getTopicString() {
    return topicString;
  }

  public void setTopicString(String topicString) {
    this.topicString = topicString;
  }

  public String getContext() {
    return context;
  }

  public void setContext(String context) {
    this.context = context;
  }

  public String getPattern() {
    return pattern;
  }

  public void setPattern(String pattern) {
    this.pattern = pattern;
  }

  public String getContextPattern() {
    return contextPattern;
  }

  public void setContextPattern(String contextPattern) {
    this.contextPattern = contextPattern;
  }
  
  public String getRootSequence() {
    return rootSequence;
  }

  public void setRootSequence(String rootSequence) {
    this.rootSequence = rootSequence;
  }
  
  public String getAcronym() {
    return acronym;
  }

  public void setAcronym(String acronym) {
    this.acronym = acronym;
  }
  
  public String getExpandedAcronym() {
    return expandedAcronym;
  }

  public void setExpandedAcronym(String expandedAcronym) {
    this.expandedAcronym = expandedAcronym;
  }
  
  public Long getOffset() {
    return offset;
  }

  public void setOffset(Long offset) {
    this.offset = offset;
  }
  
  public int compareTo(ExtractedTopic et){
    return (int) (this.getOffset() - et.getOffset());
  }
}
