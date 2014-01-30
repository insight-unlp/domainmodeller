package ie.deri.unlp.javaservices.web;

import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

import org.apache.log4j.Logger;

@Provider
public class ExceptionHandler implements ExceptionMapper<Exception> {
	
	private static Logger logger = Logger.getLogger(ExceptionHandler.class);
	
	@Override
	public Response toResponse(Exception exception) {
		//XXX: Blanket exception handler, if this is ever a front-facing service, something better will be needed.
		logger.error(exception.getMessage(), exception);
		return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
				.entity(exception.getClass().toString() + ": " + exception.getMessage()).build();
	}

}