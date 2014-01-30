package ie.deri.unlp.javaservices.textextraction;

public class Document {
	/**
	 * Unique identifier (usually filename)
	 */
	private String id;
	private String contents;
	
	public String getId() {
		return id;
	}
	public void setId(String id) {
		this.id = id;
	}
	public String getContents() {
		return contents;
	}
	public void setContents(String contents) {
		this.contents = contents;
	}
	
	public Document(String id, String contents) {
		this.id = id;
		this.contents = contents;
	}
	
	
}
