package ie.deri.unlp.javaservices.web;

import gate.util.GateException;
import ie.deri.unlp.javaservices.topicextraction.topicextractor.gate.TopicExtractorGate;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;

public class ContextInitializer implements ServletContextListener {

	@Override
	public void contextDestroyed(ServletContextEvent sce) {}

	@Override
	public void contextInitialized(ServletContextEvent sce) {
		// Initialise GATE on startup to avoid race condition and delays from first topic 
		try {
			TopicExtractorGate.getInstance().initGate();
		} catch (GateException e) {
			throw new RuntimeException(e);
		}
	}

}