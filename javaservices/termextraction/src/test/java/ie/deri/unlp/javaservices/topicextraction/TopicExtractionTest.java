package ie.deri.unlp.javaservices.topicextraction;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import gate.util.GateException;
import ie.deri.unlp.javaservices.textextraction.DocumentConversionException;
import ie.deri.unlp.javaservices.textextraction.TextExtractor;
import ie.deri.unlp.javaservices.topicextraction.data.DomainModel;
import ie.deri.unlp.javaservices.topicextraction.data.Topic;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Set;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang.StringUtils;
import org.junit.BeforeClass;
import org.junit.Test;

public class TopicExtractionTest {
	//private static Logger logger = Logger.getLogger(TopicExtractionTest.class);
	
    //For easier comparison of expected vs. actual output
    public static String asText(List<String> strings) {
        Collections.sort(strings);
        return StringUtils.join(strings, '\n');
    }
    public static List<String> getRootSequences(Collection<Topic> extractedTopics) {
        List<String> rootSequences = new ArrayList<String>();
        for (Topic extractedTopic : extractedTopics) {
            rootSequences.add(extractedTopic.getRootSequence());
        }
        return rootSequences;
    }
    private List<String> extractRootSequences(File document, DomainModel domainModel) 
    		throws DocumentConversionException, GateException, IOException {
        Set<Topic> tb = new TopicExtraction().extractTopics(document, domainModel);
        List<String> rs = getRootSequences(tb);
        return rs;
    }
    
    private static DomainModel acmDomain;
    private static DomainModel geoDomain;
    private static File sw105txt;
    private static File sw105pdf;
    
    @BeforeClass
    public static void initFiles() throws IOException {
    	acmDomain = DomainModel.fromFile(FileUtils.toFile(TopicExtractionTest.class.getResource("/acmskilltypes.lst")));
    	sw105txt = FileUtils.toFile(TopicExtractionTest.class.getResource("/semanticweb_org_pdf_105.txt"));
    	sw105pdf = FileUtils.toFile(TopicExtractionTest.class.getResource("/semanticweb_org_pdf_105.pdf"));
    	geoDomain = DomainModel.fromFile(FileUtils.toFile(TopicExtractionTest.class.getResource("/newdommodel.txt")));
    }
    
    @Test
    public void testTextExtractionSameAsPdfExtraction() throws Exception {
    	assertEquals(TextExtractor.extractText(sw105txt), TextExtractor.extractText(sw105pdf));
    	List<String> txt = extractRootSequences(sw105txt, acmDomain);
    	List<String> pdf = extractRootSequences(sw105pdf, acmDomain);
    	assertEquals(asText(txt), asText(pdf));
    }
    
    @Test
    public void testDifferentDomainModelsGiveDifferentResults() throws Exception {
    	List<String> acm = extractRootSequences(sw105txt, acmDomain);
    	List<String> geo = extractRootSequences(sw105txt, geoDomain);
    	assertTrue(!asText(acm).equals(asText(geo)));
    }
}
