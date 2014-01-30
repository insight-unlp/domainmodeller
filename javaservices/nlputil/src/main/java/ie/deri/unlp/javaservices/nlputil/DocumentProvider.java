package ie.deri.unlp.javaservices.nlputil;

public interface DocumentProvider {
    /**
     * Computes the URI of a file using its ID (only add "file//" to local path)
     *
     * @param documentUrl
     *          the ID of the document
     * @return the local path
     */
    public String offer(String documentUrl);

    /**
     * Computes the local path of a file using its ID
     *
     * @param documentUrl
     *          the ID of the document
     * @return the local path
     */
    public String offerLocalPath(String documentUrl);
}
