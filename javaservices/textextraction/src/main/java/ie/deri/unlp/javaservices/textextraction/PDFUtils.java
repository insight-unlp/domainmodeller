package ie.deri.unlp.javaservices.textextraction;

import java.io.IOException;
import java.io.InputStream;

import org.apache.tika.exception.TikaException;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.pdf.PDFParser;
import org.apache.tika.sax.BodyContentHandler;
import org.xml.sax.ContentHandler;
import org.xml.sax.SAXException;
/**
 * @author Georgeta Bordea
 * 
 */
class PDFUtils {
	//-1 for no limit on the length of input documents
	final static int MAX_CHARS = -1;

	//private static Logger logger = Logger.getLogger(PDFUtils.class.getName());

	public static String getContentPDFBox(InputStream is) throws IOException, DocumentConversionException {
		try {
			ContentHandler textHandler = new BodyContentHandler(MAX_CHARS);
			Metadata metadata = new Metadata();
			PDFParser parser = new PDFParser();
			ParseContext pc = new ParseContext();

			parser.parse(is, textHandler, metadata, pc);

			return textHandler.toString();
		} catch (SAXException | TikaException e) {
			throw new DocumentConversionException(e.getMessage(), e);
		} finally {
			is.close();
		}
	}
}
