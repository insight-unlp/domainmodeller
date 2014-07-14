package ie.deri.unlp.javaservices.textextraction;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.IOUtils;
import org.apache.log4j.Logger;
import org.apache.tika.Tika;

public class TextExtractor {
	private static Logger logger = Logger.getLogger(TextExtractor.class);

	public static String extractText(File f) throws IOException, DocumentConversionException {
		InputStream is = new FileInputStream(f);
		String mimeType = new Tika().detect(is);
		is.close();

		is = new FileInputStream(f);
		String text = extractText(is, mimeType);
		is.close();

		return text;
	}

	public static String extractText(BufferedInputStream is) throws IOException,
			DocumentConversionException {
		String detectedMimeType = new Tika().detect(is);
		is.reset(); // Go back to start of stream for re-reading
		logger.info("Detected MIME type as " + detectedMimeType);
		return extractText(is, detectedMimeType);
	}

	public static String extractText(InputStream is, String mimeType) throws IOException,
			DocumentConversionException {
		String text;
		if (mimeType.equals("text/plain")) {
			text = IOUtils.toString(is);
		} else if (mimeType.equals("application/pdf")) {
			text = PDFUtils.getContentPDFBox(is);
		} else {
			throw new UnsupportedFileTypeException("Unsupported file, unrecognised MIME type "
					+ mimeType);
		}
		return preprocessText(text);
	}

	public static String preprocessText(String content) {
		/*
		 * remove word separation characters used at the end of line, except
		 * where they occur elsewhere in the text.
		 * 
		 * e.g. "sys-\ntem" should be converted to "system" but
		 * "peer-\nto-peer" should still be "peer-to-peer", we keep the "-" if
		 * the term "peer-to-peer" appears elsewhere in the document
		 */

		Pattern whitespace = Pattern.compile(
			// Match word ending with '-' that goes on to the next line
			"(\\w+)-\\s*\\n" +
			// optional spaces or a second '-' at beginning of next line
			"\\s*-?" +
			// word including dashes on the second line
			"([\\w-]+)"
		);
		
		Matcher matcher = whitespace.matcher(content);
		StringBuffer result = new StringBuffer();
		while (matcher.find()) {
			String mergedWord = matcher.group(1) + "-" + matcher.group(2);
			if (content.contains(mergedWord)) {
				matcher.appendReplacement(result, mergedWord);
			} else {
				matcher.appendReplacement(result, "$1$2");
			}
		}
		matcher.appendTail(result);
		content = result.toString();

		return content;
	}
}
