package ie.deri.unlp.javaservices.textextraction;

import java.io.IOException;

public class DocumentConversionException extends IOException {
	private static final long serialVersionUID = 1L;

	public DocumentConversionException(String msg){
		super(msg);
	}

	public DocumentConversionException(String msg, Exception e){
		super(msg, e);
	}
}
