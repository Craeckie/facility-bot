#include "main.h"
#include <time.h>

void setClock() {
  configTime(0, 0, "de.pool.ntp.org", "pool.ntp.org");

  Serial.print("Waiting for NTP time sync: ");
  time_t now = time(nullptr);
  while (now < 2 * 3600 * 2) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println("");
  struct tm timeinfo;
  gmtime_r(&now, &timeinfo);
  Serial.print("Current time: ");
  Serial.print(asctime(&timeinfo));
}

void setup()
{
  Serial.begin(9600);
  Serial.println("Starting cloud Sensor");
  temp_sensor.begin();
  Serial.println("Connecting to WiFi..");
  connectToNetwork(); //connect to wifi network
  // Get current time to verify certificates
  setClock();

  // Check SSL Certificate:
  client.setTrustAnchors(&cert);
  //client.setInsecure();

  if (!client.connect(SERVER_HOST, SERVER_PORT_HTTPS))
  {
    Serial.println("connection failed");
  }
  else
  {
    Serial.println("Connected!");
  }
}

void loop()
{
  read_sensor_samples();
  send_temperature(get_average());

  if (WiFi.status() != WL_CONNECTED)
  { //if wifi connection lost: reconnect
    connectToNetwork();
  }
  counter++;
  if (counter > 500)
  {
    counter = 0;
    WiFi.disconnect();
    setup();
  }
}

void read_sensor_samples()
{ //reads sensor samples into a buffer
  for (int i = 0; i < SENSOR_SAMPLES; i++)
  {
    bool correct_value = false;
    while (!correct_value)
    {
      temp_sensor.requestTemperatures();
      sensor_samples[i] = temp_sensor.getTempCByIndex(0);
      if (sensor_samples[i] < 50 && sensor_samples[i] > -50)
      {
        delay(1000); //delay between each value (1 second)
        correct_value = true;
      }
    }
  }
}
float get_average()
{ //evaluates the arithmetic average of the values in the buffer
  float sum = 0;
  for (int i = 0; i < SENSOR_SAMPLES; i++)
  {
    sum += sensor_samples[i];
  }
  return sum / SENSOR_SAMPLES;
}

void send_temperature(float temperature)
{

  Serial.println(String(temperature, DECIMALS));
  if (temperature < 0)
  {
    temperature = temperature * (-1);
  }
  // Check SSL Certificate:
  client.setTrustAnchors(&cert);
  //client.setInsecure();

  //if (client.connected() || client.connect(SERVER_HOST, SERVER_PORT_HTTPS))
  if (client.connect(SERVER_HOST, SERVER_PORT_HTTPS))
  {
    Serial.println("connection established");
    client.print(String("HEAD ") + "/temp/" + String(temperature, DECIMALS) + " HTTP/1.1\r\n" +
                 "Host: " + SERVER_HOST + "\r\n" +
                 "User-Agent: ESP8266TEMPERATURSENSOR\r\n" +
                 "Authorization: Basic "+ AUTH_TOKEN + "\r\n" +
                 "Connection: close\r\n\r\n");
    while (client.connected())
    {
      String line = client.readStringUntil('\n');
      Serial.println(line);
      if (line == "\r")
      {
        Serial.println("headers received");
        break;
      }
    }

    client.stop();
  }
  else
  {
    Serial.println("Connection failed");
    client.stop();
    WiFi.disconnect();
    setup();
  }
}

void connectToNetwork()
{
  Serial.println("connecting to WiFi...");
  WiFi.begin(WIFI_SSID); //, WIFI_PASSWORD); // add password if WiFi is protected
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED && counter < 20)
  {
    delay(1000);
    counter++;
  }
  Serial.println("Connected");
  delay(500);
}
