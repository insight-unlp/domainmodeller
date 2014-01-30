package ie.deri.unlp.javaservices.textextraction;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class PreprocessingTest {
	@Test
	public void testPreprocessingContentLookup() {
		String processed = TextExtractor.preprocessText("blah peer-to-peer bl\nah semantic peer-\nto-peer");
		assertEquals("blah peer-to-peer bl\nah semantic peer-to-peer", processed);
	}
	
	@Test
	public void testPreprocessingContentLookupNegative() {
		String processed = TextExtractor.preprocessText("blah blah semantic peer-\nto-peer");
		assertEquals("blah blah semantic peerto-peer", processed);
	}
	
	@Test
	public void testPreprocessing() {
		String processed = TextExtractor.preprocessText("on-\ntology content");
		assertEquals("ontology content", processed);
	}
	
	@Test
	public void testPreprocessingWithSpaces() {
		String processed = TextExtractor.preprocessText("on-  \ntology content");
		assertEquals("ontology content", processed);
	}
	
	@Test
	public void testPreprocessingWithSpacesAndTabs() {
		String processed = TextExtractor.preprocessText("on-  \t\ntology content");
		assertEquals("ontology content", processed);
	}
	
	@Test
	public void testPreprocessingPreservesUnicode() {
		String processed = TextExtractor.preprocessText("blah \u5355\u6570");
		assertEquals("blah \u5355\u6570", processed);
	}
}
