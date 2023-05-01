package ps7.sdal.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import ps7.sdal.demo.properties.WorkersProperties;

@SpringBootApplication
@RestController
public class DemoApplication {

	// TODO: use reactive + opt path params

	@Autowired
	private RestTemplate restTemplate;

	@Autowired
	WorkersProperties workersProperties;

	public static void main(String[] args) {
		SpringApplication.run(DemoApplication.class, args);
	}

	@GetMapping("/")
	public String home() {
		return "Welcome to the PS7-AL-SD 2021/2022 project.";
	}

	@GetMapping("/predict-waiting-time/{direction}/{day}/{month}")
	public String predictWaitingTime(@PathVariable String direction, @PathVariable int day, @PathVariable int month) {
		String url = String.format("http://%s:%s/predict-waiting-time?direction=%s&day=%s&month=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), direction, day, month);
		return restTemplate.getForObject(url, String.class);
	}

	@GetMapping("/predict-waiting-time/{direction}/{day}/{month}/{year}")
	public String predictWaitingTimeYear(@PathVariable String direction, @PathVariable int day, @PathVariable int month,
									 @PathVariable int year) {
		String url = String.format("http://%s:%s/predict-waiting-time?direction=%s&day=%s&month=%s&year=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), direction, day, month,
				year);
		return restTemplate.getForObject(url, String.class);
	}

	@GetMapping("/predict-waiting-time/{direction}/{day}/{month}/{year}/{hour}")
	public String predictWaitingTimeHour(@PathVariable String direction, @PathVariable int day, @PathVariable int month,
										 @PathVariable int year, @PathVariable int hour) {
		String url = String.format("http://%s:%s/predict-waiting-time?direction=%s&day=%s&month=%s&year=%s&hour=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), direction, day, month,
				year, hour);
		return restTemplate.getForObject(url, String.class);
	}

	@GetMapping("/predict-number/{vehicule}/{direction}/{day}/{month}")
	public String predictNumberCars(@PathVariable String vehicule, @PathVariable String direction,
									@PathVariable int day, @PathVariable int month) {
		String url = String.format("http://%s:%s/predict-number-%s?direction=%s&day=%s&month=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), vehicule, direction, day,
				month);
		return restTemplate.getForObject(url, String.class);
	}

	@GetMapping("/predict-number/{vehicule}/{direction}/{day}/{month}/{year}")
	public String predictNumberCarsYear(@PathVariable String vehicule, @PathVariable String direction,
										@PathVariable int day, @PathVariable int month, @PathVariable int year) {
		String url = String.format("http://%s:%s/predict-number-%s?direction=%s&day=%s&month=%s&year=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), vehicule, direction, day,
				month, year);
		return restTemplate.getForObject(url, String.class);
	}

	@GetMapping("/predict-number/{vehicule}/{direction}/{day}/{month}/{year}/{hour}")
	public String predictNumberCarsHour(@PathVariable String vehicule, @PathVariable String direction,
										@PathVariable int day, @PathVariable int month, @PathVariable int year,
										@PathVariable int hour) {
		String url = String.format("http://%s:%s/predict-number-%s?direction=%s&day=%s&month=%s&year=%s&hour=%s",
				workersProperties.getHostNames().get(0), workersProperties.getPorts().get(0), vehicule, direction, day,
				month, year, hour);
		return restTemplate.getForObject(url, String.class);
	}

	@PostMapping("/import_controls")
	public String handleFileUpload(@RequestParam("file") MultipartFile file, RedirectAttributes redirectAttributes) {
		MultiValueMap<String, Object> bodyMap = new LinkedMultiValueMap<>();
		bodyMap.add("file", file.getResource());
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.MULTIPART_FORM_DATA);
		HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(bodyMap, headers);
		restTemplate.exchange(String.format("http://%s:%s/batch_process/controls",
						workersProperties.getHostNames().get(1), workersProperties.getPorts().get(1)),
				HttpMethod.POST, requestEntity, String.class);
		restTemplate.exchange(String.format("http://%s:%s/speed_process/controls",
						workersProperties.getHostNames().get(2), workersProperties.getPorts().get(2)),
				HttpMethod.POST, requestEntity, String.class);

		redirectAttributes.addFlashAttribute("message",
				"You successfully uploaded " + file.getOriginalFilename() + "!");
		return "redirect:/";
	}
}
