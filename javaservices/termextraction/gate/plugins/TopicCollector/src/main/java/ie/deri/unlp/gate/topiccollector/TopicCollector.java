/*
 *  TopicCollector.java
 *
 *
 * Copyright (c) 2000-2001, The University of Sheffield.
 *
 * This file is part of GATE (see http://gate.ac.uk/), and is free
 * software, licenced under the GNU Library General Public License,
 * Version 2, June1991.
 *
 * A copy of this licence is included in the distribution in the file
 * licence.html, and is also available at http://gate.ac.uk/gate/licence.html.
 *
 *  alesch, 20/2/2009
 *
 *  $Id: TopicCollector.jav 9992 2008-10-31 16:53:29Z ian_roberts $
 *
 * For details on the configuration options, see the user guide:
 * http://gate.ac.uk/cgi-bin/userguide/sec:creole-model:config
 */

package ie.deri.unlp.gate.topiccollector;

import gate.Annotation;
import gate.AnnotationSet;
import gate.FeatureMap;
import gate.ProcessingResource;
import gate.Resource;
import gate.creole.AbstractLanguageAnalyser;
import gate.creole.ExecutionException;
import gate.creole.ResourceInstantiationException;
import gate.creole.metadata.CreoleResource;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * This class is the implementation of the resource TOPIC COLLECTOR.
 */
@CreoleResource(name = "Topic Collector", comment = "Resource used to collect the extracted topics")
public class TopicCollector extends AbstractLanguageAnalyser implements
    ProcessingResource, Serializable {

  /**
	 * 
	 */
  private static final long serialVersionUID = -6526769123531395877L;

  private static Logger logger =
      Logger.getLogger(TopicCollector.class.getName());

  public TopicCollector() {
  }

  @Override
  public Resource init() throws ResourceInstantiationException {

    return this;
  }

  @Override
  public void execute() throws ExecutionException {

    /**
     * we store the identified topics for the document here
     */
    List<ExtractedTopicImpl> extractedTopics =
        new ArrayList<ExtractedTopicImpl>();

    // we store the numbers of tokens in the document here
    Integer tokensNumber = 0;

    // we collect and count the topics here

    // get the annotationSet name provided by the user, or fail

    AnnotationSet topics = null;
    AnnotationSet tokens = null;
    AnnotationSet acronyms = null;
    AnnotationSet expansions = null;

    try {
      topics = document.getAnnotations().get(topicAnnotationSetName);
      tokens = document.getAnnotations().get(TOKEN_ANNOTATION_TYPE);
      expansions = document.getAnnotations().get(EXPANSION_ANNOTATION_SET_NAME);
      if (tokens != null) {
        tokensNumber = tokens.size();
      }
    } catch (Exception exn) {
      logger.log(Level.WARNING, "could not access topic annotation set : "
          + exn.getMessage());
      throw new ExecutionException(exn);
    }

    // build the map with the acronyms and expanded acronyms
    Map<String, String> expMap = new HashMap<String, String>();

    if (expansions != null) {
      Iterator<Annotation> expItr = expansions.iterator();
      while (expItr.hasNext()) {
        Annotation expAnnot = expItr.next();
        FeatureMap topicFeatures = expAnnot.getFeatures();
        String expandedAcronym =
            (String) topicFeatures.get(EXPANDED_ACRONYM_FEATURE_NAME);
        String acronym = (String) topicFeatures.get(ACRONYM_FEATURE_NAME);
        expMap.put(expandedAcronym, acronym);
        // logger.log(Level.INFO, acronym + " -> " + expandedAcronym);
      }
    }

    // build the map with the topic annotations and features
    if (topics != null) {
      Iterator<Annotation> topicItr = topics.iterator();
      while (topicItr.hasNext()) {
        Annotation topicAnnot = topicItr.next();
        FeatureMap topicFeatures = topicAnnot.getFeatures();

        String topicString =
            (String) topicFeatures.get(topicTextualRepresentationFeatureName);
        String context =
            (String) topicFeatures
                .get(SEGMENT_TEXTUAL_REPRESENTATION_FEATURE_NAME);
        String pattern = (String) topicFeatures.get(POS_SEQUENCE_FEATURE_NAME);
        String rootSequence =
            (String) topicFeatures.get(ROOT_SEQUENCE_FEATURE_NAME);
        String contextPattern =
            (String) topicFeatures
                .get(CONTEXT_TEXTUAL_REPRESENTATION_FEATURE_NAME);
        Long offset = (Long) topicFeatures.get(OFFSET_FEATURE_NAME);

        String expandedTopic = null;
        String acronym = null;

        Set<String> keySet = expMap.keySet();
        for (String key : keySet) {
          String expTopicCandidate = key;
          String acronymCandidate = expMap.get(key);
          if (topicString.equalsIgnoreCase(expTopicCandidate)) {
            acronym = acronymCandidate;
          }
          if (topicString.equals(acronymCandidate)) {
            expandedTopic = expTopicCandidate;
          }
        }

        ExtractedTopicImpl extractedTopic =
            new ExtractedTopicImpl(topicString, context, pattern,
                contextPattern, rootSequence, acronym, expandedTopic, offset);

        extractedTopics.add(extractedTopic);
      }
    }

    // adding to gate.document
    document.getFeatures().put(topicsListFeatureName, extractedTopics);
    document.getFeatures().put(tokensNumberFeatureName, tokensNumber);
  }

  /*
   * GETTERS AND SETTERS
   */

  public String getTopicTextualRepresentationFeatureName() {
    return topicTextualRepresentationFeatureName;
  }

  public void setTopicTextualRepresentationFeatureName(
      String topicTextualRepresentationFeatureName) {
    this.topicTextualRepresentationFeatureName =
        topicTextualRepresentationFeatureName;
  }

  /**
   * Set the name of the annotation set to place the generated Token annotations
   * in.
   */
  public void setTopicAnnotationSetName(String annotationSetName) {
    this.topicAnnotationSetName = annotationSetName;
  }

  /**
   * Return the annotation set name used for the Tokens.
   */
  public String getTopicAnnotationSetName() {
    return topicAnnotationSetName;
  }

  public String getTokensNumberFeatureName() {
    return tokensNumberFeatureName;
  }

  public void setTokensNumberFeatureName(String tokensNumberFeatureName) {
    this.tokensNumberFeatureName = tokensNumberFeatureName;
  }

  public String getTopicsListFeatureName() {
    return topicsListFeatureName;
  }

  public void setTopicsListFeatureName(String topicsListFeatureName) {
    this.topicsListFeatureName = topicsListFeatureName;
  }

  private String topicTextualRepresentationFeatureName;
  private String topicAnnotationSetName;
  private String tokensNumberFeatureName;// = "tokensNumber";
  private String topicsListFeatureName;// = "topicsList";

  private static final String POS_SEQUENCE_FEATURE_NAME = "POSsequence";
  private static final String ROOT_SEQUENCE_FEATURE_NAME = "RootSequence";
  private static final String CONTEXT_TEXTUAL_REPRESENTATION_FEATURE_NAME =
      "contextTextualRepresentation";
  private static final String SEGMENT_TEXTUAL_REPRESENTATION_FEATURE_NAME =
      "segmentTextualRepresentation";
  private static final String EXPANSION_ANNOTATION_SET_NAME = "Expansion";
  private static final String EXPANDED_ACRONYM_FEATURE_NAME = "matchedTokens";
  private static final String ACRONYM_FEATURE_NAME = "acronym";
  private static final String OFFSET_FEATURE_NAME = "offset";
} // class TopicCollector
