FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /build

COPY backend/pom.xml .

RUN mvn -B -DskipTests dependency:go-offline

COPY backend/src ./src

RUN mvn -B -DskipTests package


FROM eclipse-temurin:21-jre-jammy

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=build /build/target/backend-0.0.1-SNAPSHOT.jar /app/backend.jar

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=45s --retries=5 \
    CMD curl -fsS http://localhost:8080/api/infrastructure/health || exit 1

ENTRYPOINT ["java", "-jar", "/app/backend.jar"]