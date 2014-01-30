package ie.deri.unlp.javaservices.nlputil;
public class WordUtils {

    public static Integer computeTokensNo(String s) {
        return s.split(" ").length;
    }

    public static Integer minimumWordLength(String[] words) {
        Integer minLength = Integer.MAX_VALUE;

        for (String word : words) {
            if (minLength > word.length()) {
                minLength = word.length();
            }
        }
        return minLength;
    }

    public static boolean isAlpha(final char c) {
        return ((c >= 'a') && (c <= 'z')) || ((c >= 'A') && (c <= 'Z'));
    }

    public static boolean isAlphaNumeric(final char c) {
        return ((c >= 'a') && (c <= 'z')) || ((c >= 'A') && (c <= 'Z')) || ((c >= '0') && (c <= '9'));
    }

}
