package ie.deri.unlp.javaservices.web;

import static org.junit.Assert.assertEquals;
import gate.util.GateException;
import ie.deri.unlp.javaservices.textextraction.DocumentConversionException;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;

import javax.ws.rs.core.MediaType;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.Logger;
import org.junit.Test;

import com.sun.jersey.api.client.WebResource;
import com.sun.jersey.multipart.FormDataBodyPart;
import com.sun.jersey.multipart.FormDataMultiPart;
import com.sun.jersey.test.framework.JerseyTest;
import com.sun.jersey.test.framework.WebAppDescriptor;

public class RestTest extends JerseyTest {
	Logger logger = Logger.getLogger(RestTest.class);

	public RestTest() {
        super(new WebAppDescriptor.Builder(RestService.class.getPackage().getName())
        .build());
	}
	
	@Test
	public void testTextExtraction() throws DocumentConversionException, FileNotFoundException,
			IOException, GateException {
        WebResource webResource = resource();
        File f = FileUtils.toFile(RestTest.class.getResource("/simple.pdf"));
        WebResource path = webResource.path("textextraction");
        
        FormDataMultiPart form = new FormDataMultiPart();
        InputStream content = new FileInputStream(f);
        FormDataBodyPart fdp = new FormDataBodyPart("document", content, 
        		MediaType.APPLICATION_OCTET_STREAM_TYPE);
        form.bodyPart(fdp);

        String text = path.type(MediaType.MULTIPART_FORM_DATA).post(String.class, form);
        content.close();
		assertEquals("A simple PDF with 单数 UTF-8 character", text.trim());
	}
	
	@Test
	public void testHelloWorld() throws DocumentConversionException, FileNotFoundException,
			IOException, GateException {
		//Sanity test
		WebResource path = resource().path("helloWorld");
		assertEquals("Hello world!", path.get(String.class));
	}
	
}
