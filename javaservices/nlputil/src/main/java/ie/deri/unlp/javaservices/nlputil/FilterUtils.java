package ie.deri.unlp.javaservices.nlputil;

import java.beans.Introspector;
import java.io.IOException;
import java.util.Set;


public class FilterUtils {
    private static Set<String> stopWords;
    static {
        try {
            stopWords = new StopWordsFromResource("/stopwords.txt").getStopWords();
        } catch (IOException e) {
            throw new RuntimeException("Missing stopwords resource");
        }
    }


    public static boolean isProperTopic(String rootSequence) {
        String s = rootSequence;

        if (s.length() < 2) {
            return false;
        }
        // all words need to have at least 2 characters
        String[] words = s.split(" ");
        if (WordUtils.minimumWordLength(words) < 2) {
            return false;
        }

        if (s.contains("- ") || s.contains(" -")) {
            return false;
        }
        final char[] chars = s.toCharArray();

        // first character must be alphabetic
        if (!WordUtils.isAlpha(chars[0])) {
            return false;
        }
        if (!WordUtils.isAlphaNumeric(chars[chars.length - 1])) {
            return false;
        }

        // first or last word not in stopwords
    	String firstWord = Introspector.decapitalize(words[0]);
    	String lastWord = Introspector.decapitalize(words[words.length-1]);
    	if (stopWords.contains(firstWord) || stopWords.contains(lastWord)) {
            return false;
        }

        // is alpha numeric
        for (int x = 0; x < chars.length; x++) {
            final char c = chars[x];
            if (!WordUtils.isAlphaNumeric(c) && c != '-' && c != ' ') {
                return false;
            }
        }
        return true;
    }
}
