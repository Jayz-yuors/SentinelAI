package com.sentinelai.backend.common.config;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class JacksonConfig {

    @Bean
    public ObjectMapper objectMapper() {

        ObjectMapper mapper = new ObjectMapper();

        /*
         * Allow JSON responses to contain fields that
         * may not yet exist in a Java DTO.
         */
        mapper.configure(
                DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES,
                false
        );

        /*
         * Do not fail when a response contains an empty
         * object/collection that is not strictly required.
         */
        mapper.configure(
                SerializationFeature.FAIL_ON_EMPTY_BEANS,
                false
        );

        return mapper;
    }
}