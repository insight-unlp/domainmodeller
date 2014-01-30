package ie.deri.unlp.javaservices.nlputil;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.io.IOUtils;

public class StopWordsFromResource implements StopWords {
    private Set<String> stopWords;
    public Set<String> getStopWords() {
        return stopWords;
    }

    public StopWordsFromResource(String path) throws IOException {
    	InputStream is = this.getClass().getResourceAsStream(path);
    	try {
    		stopWords = new HashSet<String>(IOUtils.readLines(is));
    	} finally {
    		is.close();
    	}
    }
}