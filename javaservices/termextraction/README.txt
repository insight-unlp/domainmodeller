========
Building
========

When making changes to the GATE files, you must recompile the termextraction project
so that the files are copied to the target folder.

	barcou@barcou:~/code/saffronservices$ mvn compile -pl termextraction -am
	
If you make changes to the .java files in gate/, you must `mvn compile` from gate/ first.

===================================
Term extraction high-level overview
===================================
2013-05-08
Edit link: http://www.asciiflow.com/#Draw2145182520258297230/440352145



   +------------------+                                                        +----------------+
   |                  |                                                        |                |
   |                  |                                                        |                |
   | TopicExtraction  |                                                        | TopicAdaptor   |
   |                  |    +--------------+         +------------+             |                |
   |                  |---->TopicExtractor+--------->TopicsFilter+------------>|                |
   +------------------+    +--------------+         +------------+             +---------+------+
       ^        ^                                                List<ExtractedTopic>    |
       |        |                                                                        |
       |        |                                                                        |
       +        +                                                                        |
File document  DomainModel domainModel                                                   v
    *or*                                                                               Set<Topic>
 String text                                                                                   
                                                                                   
TopicExtraction		Encapsulates the whole term extraction process.
TopicExtractor		GATE application returning List<ExtractedTopic>
TopicsFilter		Filter ExtractedTopics (see AllFilters.java)
DocumentSearcher	Searchable index of the document (not stemmed as it is used to count occurrences
					of morphological variations)
TopicAdaptor		Convert data into Topic objects which are more user-friendly and contain
					information about the number of occurrences and morphological variation of terms.