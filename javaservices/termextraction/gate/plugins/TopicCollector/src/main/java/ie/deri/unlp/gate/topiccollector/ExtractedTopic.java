/**
 * 
 */
package ie.deri.unlp.gate.topiccollector;

/**
 * @author Georgeta Bordea
 *
 */

public interface ExtractedTopic extends Comparable<ExtractedTopic> {
  public String getTopicString();
  public String getContext();
  public String getPattern();
  public String getContextPattern();
  public String getRootSequence();
  public String getAcronym();
  public String getExpandedAcronym();
  public Long getOffset();
  public int compareTo(ExtractedTopic et);
}
