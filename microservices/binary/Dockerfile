FROM maven:3.8.4-openjdk-8-slim as build
COPY src /tmp/src
COPY pom.xml /tmp/
WORKDIR /tmp
RUN mvn install
RUN mvn clean package

FROM openjdk:8-jdk as main
COPY --from=build /tmp/target/binary-1.0-SNAPSHOT-jar-with-dependencies.jar /usr/local/binary/binary.jar
WORKDIR /usr/local/binary

EXPOSE 8080
ENTRYPOINT ["java","-jar","binary.jar"]
