package ie.deri.unlp.javaservices.web;

import gate.util.GateException;
import ie.deri.unlp.javaservices.textextraction.DocumentConversionException;
import ie.deri.unlp.javaservices.textextraction.TextExtractor;
import ie.deri.unlp.javaservices.topicextraction.TopicExtraction;
import ie.deri.unlp.javaservices.topicextraction.data.DomainModel;
import ie.deri.unlp.javaservices.topicextraction.data.Topic;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import javax.ws.rs.Consumes;
import javax.ws.rs.FormParam;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import org.apache.commons.io.IOUtils;
import org.apache.log4j.Logger;

import com.sun.jersey.multipart.FormDataBodyPart;
import com.sun.jersey.multipart.FormDataParam;

@Path("/")
@Produces({MediaType.APPLICATION_JSON, MediaType.APPLICATION_XML})
public class RestService {
	private static Logger logger = Logger.getLogger(RestService.class);
	
    @GET
    @Path("/helloWorld")
    public String helloWorld() {
        return "Hello world!";
    }

	
    TopicExtraction te;
    public RestService() throws GateException {
    	te = new TopicExtraction();
    }
    
    /**
     * Request for term extraction with a document file and domain model file.as a query parameters.
     * This method is primarily for the HTML tester interface. 
     * 
     * Sample usage:
     * curl -X POST --form "document=@mydocument.pdf;type=application/pdf" 
     *   --form domainModel=@mydomainmodel.txt http://localhost:8082/api/termextraction/files 
     */
    @POST @Path("/termextraction/files") //Need separate URL because it clashes with the File & List<String> method
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    public Set<Topic> extractTopics(
    	@FormDataParam("document") InputStream document,
    	@FormDataParam("document") FormDataBodyPart documentDetails,
    	@FormDataParam("domainModel") InputStream domainModel) throws IOException, DocumentConversionException, GateException {

    	logger.info("Document MIME type: " + documentDetails.getMediaType().toString());
    	
    	//Hack to read whole stream, avoids "stream already closed" errors (possible a Jersey timeout feature?)
    	InputStream documentStream = IOUtils.toBufferedInputStream(document);
    	InputStream domainStream = IOUtils.toBufferedInputStream(domainModel);
    	
    	try {
    		String textContent = TextExtractor.extractText(documentStream, documentDetails.getMediaType().toString());
    		DomainModel model = DomainModel.fromStream(domainStream);
    		
    		Set<Topic> topics = te.extractTopics(textContent, model);
            return topics;
    	} finally {
    		documentStream.close();
    		domainStream.close();
    	}
    }

    /**
     * Request for term extraction with a plain-text document string with domain model as a query pattern.
     * 
     * curl -X POST --form "document=An algorithm for complexity of something" 
     *   --form domainModel=algorithm --form domainModel=complexity http://localhost:8082/api/termextraction
     */
    @POST @Path("/termextraction")
    @Consumes(MediaType.APPLICATION_FORM_URLENCODED)
    public Set<Topic> extractTopics(@FormParam("document") String plainText, @FormParam("domainModel") List<String> domainWords) 
    		throws GateException, IOException {
        
    	DomainModel domainModel = new DomainModel(domainWords);
    	plainText = TextExtractor.preprocessText(plainText);
    	Set<Topic> topics = te.extractTopics(plainText, domainModel);
        return topics;
    }
    
    /**
     * Request for term extraction with a document file with domain model as query parameters.
     * 
     * Sample request:
     * curl -X POST --form "document=@mydoc.pdf;type=application/pdf" 
     *    --form domainModel=word1 --form domainModel=word2 http://localhost:8082/api/termextraction
     */
    @POST @Path("/termextraction")
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    public Set<Topic> extractTopics(
    		@FormDataParam("document") InputStream document,
        	@FormDataParam("document") FormDataBodyPart documentDetails,
        	@FormDataParam("domainModel") List<FormDataBodyPart> domainWordsBody) throws GateException, IOException {
        
    	List<String> domainWords = new ArrayList<String>();
    	for (FormDataBodyPart vPart : domainWordsBody) {
    	    domainWords.add(vPart.getValueAs(String.class));
    	}
    	
    	DomainModel domainModel = new DomainModel(domainWords);
    	logger.info("Processing document with domainModel " + domainModel);
    	InputStream bufferedInputStream = IOUtils.toBufferedInputStream(document);
    	Set<Topic> topics = te.extractTopics(bufferedInputStream, documentDetails.getMediaType().toString(), domainModel);
    	bufferedInputStream.close();
        return topics;
    }
    
    /**
     * Request for text extraction from a file
     * 
     * Sample request:
     * curl -X POST --form "document=@mydoc.pdf;type=application/pdf" http://localhost:8082/api/textextraction
     */
    @POST @Path("/textextraction")
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    @Produces(MediaType.TEXT_PLAIN + ";charset=utf-8")
    public String extractText(
    		@FormDataParam("document") InputStream document) throws DocumentConversionException, IOException {
    	BufferedInputStream bufferedInputStream = new BufferedInputStream(IOUtils.toBufferedInputStream(document));
    	try {
    		return TextExtractor.extractText(bufferedInputStream);
    	} finally {
    		bufferedInputStream.close();
    	}
    }
    
}
