package ie.deri.unlp.javaservices.nlputil;

/**
 * @author Georgeta Bordea
 *
 */
public class GenericDocumentProvider implements DocumentProvider {

    /*
     * (non-Javadoc)
     *
     * @see
     * ie.deri.unlp.expertisemining.core.rdfextract.DocumentProvider#offer(java
     * .lang.String)
     */
    @Override
    public String offer(String documentPath) {
        return "file:///" + documentPath.substring(documentPath.indexOf('/') + 1);
    }

    /*
     * (non-Javadoc)
     *
     * @see
     * ie.deri.unlp.expertisemining.core.rdfextract.DocumentProvider#offerLocalPath
     * (java.lang.String)
     */
    @Override
    public String offerLocalPath(String documentUrl) {
        // TODO Auto-generated method stub
        return null;
    }

}
