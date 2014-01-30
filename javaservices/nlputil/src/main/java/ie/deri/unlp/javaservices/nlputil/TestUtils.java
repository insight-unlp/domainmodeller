package ie.deri.unlp.javaservices.nlputil;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collection;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.DirectoryFileFilter;
import org.apache.commons.io.filefilter.TrueFileFilter;

/**
 * Utility functions for working with resources (for JUnit tests only, will not work with JAR files)
 * @author barcou
 *
 */
public class TestUtils {
    public static String readResourceToString(String path, Class<?> clazz) throws IOException {
        return FileUtils.readFileToString(resourceAsFile(path, clazz));
    }

    public static File resourceAsFile(String fileName, Class<?> clazz) {
        try {
        	URI url = clazz.getResource(fileName).toURI();
            return new File(url);
        } catch (URISyntaxException e) {
            //We don't expect this to occur anyways
            throw new IllegalArgumentException(e);
        }
    }

    public static Collection<File> allResources(String folder, Class<?> clazz) {
        return FileUtils.listFiles(
                resourceAsFile(folder, clazz),
                TrueFileFilter.TRUE,
                DirectoryFileFilter.DIRECTORY
        );
    }
}
