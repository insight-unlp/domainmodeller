package ie.deri.unlp.javaservices.web;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.util.resource.Resource;
import org.eclipse.jetty.webapp.WebAppContext;

public class SaffronServicesServer {
	public static void main(String[] args) throws Exception{
		int port = (args.length > 1) ? Integer.parseInt(args[1]) : 8082; 
        Server server = new Server(port);
        
        WebAppContext webapp = new WebAppContext();
        //Generic way of pointing to web.xml instead of using setWar("./target/classes")
        webapp.setBaseResource(Resource.newClassPathResource("./"));
        server.setHandler(webapp);
        
        server.start();
        server.join();
	}
}
