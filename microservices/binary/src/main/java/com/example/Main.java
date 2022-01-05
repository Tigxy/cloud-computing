package com.example;

import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;

/**
 * Main class.
 *
 */
public class Main {
    public static final String BASE_URI = "http://0.0.0.0";

    public static final String MICROSERVICE_PORT = System.getenv("MICROSERVICE_PORT");

    private static final Logger logger = LoggerFactory.getLogger(Main.class);

    private static final MainService mainService = new MainService();


    /**
     * Starts Grizzly HTTP server exposing JAX-RS resources defined in this application.
     * @return Grizzly HTTP server.
     */
    public static HttpServer startServer(final String port) {
        // create a resource config that scans for JAX-RS resources and providers
        // in com.example package
        final ResourceConfig rc = new ResourceConfig().packages("com.example");

        // create and start a new instance of grizzly http server
        // exposing the Jersey application at BASE_URI
        return GrizzlyHttpServerFactory.createHttpServer(URI.create(String.format("%s:%s", BASE_URI, port)), rc);
    }

    /**
     * Main method.
     * @param args
     * @throws IOException
     */
    public static void main(String[] args) throws IOException, InterruptedException {

        //final String port = System.getenv("MICROSERVICE_PORT");
        //final String mainServiceUrl = System.getenv("MAIN_SERVICE_URL");
        // final STring mainServicePort = System.getenv("MAIN_SERVICE_PORT");

        //final String port = "8080";

        if (null == MICROSERVICE_PORT) {
            logger.info("No MICROSERVICE_PORT env specified...");
            return;
        }


        while (!mainService.isRegistered()) {
            mainService.register("binary", MICROSERVICE_PORT);

            try {
                Thread.sleep(10);
            } catch(InterruptedException ex) {
                Thread.currentThread().interrupt();
            }
        }


        final HttpServer server = startServer(MICROSERVICE_PORT);

        // shutdown hook: https://stackoverflow.com/questions/14558079/grizzly-http-server-should-keep-running
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("Stopping server..");
            server.shutdown();
        }, "shutdownHook"));

        try {
            logger.info("Starting server..");
            server.start();
            Thread.currentThread().join();
        } catch (Exception e) {
            logger.error("Error while starting server.", e);
        }
    }
}