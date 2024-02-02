#include <Arduino.h>
#include <ESP8266WiFi.h>
//#include <ESP8266mDNS.h>
//#include <WiFiUdp.h>
//#include <OneWire.h>
#include <DallasTemperature.h>

#include "config.h" //personal configuration of the sensor

//prototypen
void connectToNetwork();
void read_sensor_samples();
inline float get_average();
void send_temperature(float temperature);

//global Objects and attributes
BearSSL::WiFiClientSecure client;
OneWire oneWire(ONEWIRE_GPIO);
DallasTemperature temp_sensor(&oneWire);
float sensor_samples[SENSOR_SAMPLES];
int counter = 0;