package ps7.sdal.demo.properties;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
@ConfigurationProperties(prefix = "workers")
@Data
public class WorkersProperties {

    private List<String> hostNames;
    private List<Integer> ports;
}
