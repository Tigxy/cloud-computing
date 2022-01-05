FROM openjdk:8-jdk
#RUN apt-get update
#RUN apt-get install -y maven
#COPY pom.xml /usr/local/gifme/pom.xml
#COPY src /usr/local/gifme/src
COPY target/binary-1.0-SNAPSHOT-jar-with-dependencies.jar /usr/local/binary/binary.jar
WORKDIR /usr/local/binary
#RUN mvn package

EXPOSE 8080

CMD ["ls -la"]
CMD ["java","-cp","binary.jar", "com.example.Main"]
