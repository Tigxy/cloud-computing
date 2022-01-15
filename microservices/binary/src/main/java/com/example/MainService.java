package com.example;

import jakarta.ws.rs.ProcessingException;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.Form;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import org.glassfish.jersey.client.internal.HttpUrlConnector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MainService {

    /*private static final String MAIN_SERVICE_URL = System.getenv("MAIN_SERVICE_URL");
    private static final String MAIN_SERVICE_PORT = System.getenv("MAIN_SERVICE_PORT");
    private static final String MAIN_SERVICE_URL = System.getenv("MAIN_SERVICE_URL");
    */
    private static final String INGRESS_HOST = System.getenv("INGRESS_HOST");

    private static final Logger logger = LoggerFactory.getLogger(MainService.class);

    private boolean registered = false;

    public boolean isRegistered() {
        return registered;
    }

    public void register(final String command, final String port) throws ProcessingException {

        if (null == INGRESS_HOST) {
            logger.warn("No INGRESS_HOST environment variable specified..");
            return;
        }

        Form form = new Form();
        form.param("command", command);
        form.param("port", port);

        Client client = ClientBuilder.newClient();
        Entity entity = Entity.entity(form, MediaType.APPLICATION_FORM_URLENCODED_TYPE);
        Response response = client.target(INGRESS_HOST)
                                .path("register")
                                .request(MediaType.TEXT_PLAIN)
                                .post(entity);


        String result = response.readEntity(String.class);
        if (200 != response.getStatus() && !result.equals("OK")) {
            logger.warn(String.format("Could not register %s command - Response Status: %d, Response.result: %s",
                command, response.getStatus(), result));
            return;
        }

        this.registered = true;
    }

}
