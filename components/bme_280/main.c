/*
  Comple：make
  Run: ./bme280
  
  This Demo is tested on Raspberry PI 3B+
  you can use I2C or SPI interface to test this Demo
  When you use I2C interface,the default Address in this demo is 0X77
  When you use SPI interface,PIN 27 define SPI_CS
*/
#include "bme280.h"
#include <stdio.h>
#include <unistd.h>
#include <curl/curl.h>
#include <string.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <fcntl.h>
//Raspberry 3B+ platform's default I2C device file
#define IIC_Dev  "/dev/i2c-1"

//Raspberry 3B+ platform's default SPI channel
#define channel 0  

//Default write it to the register in one time
#define USESPISINGLEREADWRITE 0 

//This definition you use I2C or SPI to drive the bme280
//When it is 1 means use I2C interface, When it is 0,use SPI interface
#define USEIIC 1

	
int fd;

void user_delay_ms(uint32_t period)
{
  usleep(period*1000);
}

int8_t user_i2c_read(uint8_t id, uint8_t reg_addr, uint8_t *data, uint16_t len)
{
  write(fd, &reg_addr,1);
  read(fd, data, len);
  return 0;
}

int8_t user_i2c_write(uint8_t id, uint8_t reg_addr, uint8_t *data, uint16_t len)
{
  int8_t *buf;
  buf = malloc(len +1);
  buf[0] = reg_addr;
  memcpy(buf +1, data, len);
  write(fd, buf, len +1);
  free(buf);
  return 0;
}

void print_sensor_data(struct bme280_data *comp_data)
{
	printf("temperature:%0.2f*C   pressure:%0.2fhPa   humidity:%0.2f%%\r\n",comp_data->temperature, comp_data->pressure/100, comp_data->humidity);
}

int8_t stream_sensor_data_forced_mode(struct bme280_dev *dev)
{
    int8_t rslt;
    uint8_t settings_sel;
    struct bme280_data comp_data;

    /* Recommended mode of operation: Indoor navigation */
    dev->settings.osr_h = BME280_OVERSAMPLING_1X;
    dev->settings.osr_p = BME280_OVERSAMPLING_16X;
    dev->settings.osr_t = BME280_OVERSAMPLING_2X;
    dev->settings.filter = BME280_FILTER_COEFF_16;

    settings_sel = BME280_OSR_PRESS_SEL | BME280_OSR_TEMP_SEL | BME280_OSR_HUM_SEL | BME280_FILTER_SEL;

    rslt = bme280_set_sensor_settings(settings_sel, dev);

    printf("Temperature           Pressure             Humidity\r\n");
    /* Continuously stream sensor data */
    while (1) {
        rslt = bme280_set_sensor_mode(BME280_FORCED_MODE, dev);
        /* Wait for the measurement to complete and print data @25Hz */
        dev->delay_ms(40);
        rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, dev);
        print_sensor_data(&comp_data);
    }
    return rslt;
}


int8_t stream_sensor_data_normal_mode(struct bme280_dev *dev)
{
	int8_t rslt;
	uint8_t settings_sel;
	struct bme280_data comp_data;

	/* Recommended mode of operation: Indoor navigation */
	dev->settings.osr_h = BME280_OVERSAMPLING_1X;
	dev->settings.osr_p = BME280_OVERSAMPLING_16X;
	dev->settings.osr_t = BME280_OVERSAMPLING_2X;
	dev->settings.filter = BME280_FILTER_COEFF_16;
	dev->settings.standby_time = BME280_STANDBY_TIME_62_5_MS;

	settings_sel = BME280_OSR_PRESS_SEL;
	settings_sel |= BME280_OSR_TEMP_SEL;
	settings_sel |= BME280_OSR_HUM_SEL;
	settings_sel |= BME280_STANDBY_SEL;
	settings_sel |= BME280_FILTER_SEL;
	rslt = bme280_set_sensor_settings(settings_sel, dev);
	rslt = bme280_set_sensor_mode(BME280_NORMAL_MODE, dev);

	printf("Temperature           Pressure             Humidity\r\n");
	while (1) {
		/* Delay while the sensor completes a measurement */
		dev->delay_ms(5000);
		rslt = bme280_get_sensor_data(BME280_ALL, &comp_data, dev);
		send_temp_reading(comp_data.temperature, comp_data.humidity, comp_data.pressure);
		print_sensor_data(&comp_data);
	}

	return rslt;
}




void send_api_request(char* endpoint[], char* json_data) {

	char url[127] = "http://192.168.0.135:8000/";

	struct curl_slist *headers = NULL;
	headers = curl_slist_append(headers, "Accept: application/json");
	headers = curl_slist_append(headers, "Content-Type: application/json");
	headers = curl_slist_append(headers, "charset: utf-8");

	CURL *curl = curl_easy_init();
	curl_easy_setopt(curl, CURLOPT_URL, strcat(url, endpoint));
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);
	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);



	curl_easy_perform(curl);
}



void send_temp_reading(double temp, double humidity, double pressure) {

	char json[512];

	sprintf(json, "{\n\"temperature\" : %0.2f,\n \"humidity\" : %0.2f \n,\n \"pressure\" : %0.2f \n}", temp, humidity, pressure);

	send_api_request("temperature/external", json);
}

int main(int argc, char* argv[])
{


  struct bme280_dev dev;
  int8_t rslt = BME280_OK;

  if ((fd = open(IIC_Dev, O_RDWR)) < 0) {
    printf("Failed to open the i2c bus %s", argv[1]);
    exit(1);
  }
  if (ioctl(fd, I2C_SLAVE, 0x77) < 0) {
    printf("Failed to acquire bus access and/or talk to slave.\n");
    exit(1);
  }
  dev.dev_id = BME280_I2C_ADDR_SEC; //0x77
  dev.intf = BME280_I2C_INTF;
  dev.read = user_i2c_read;
  dev.write = user_i2c_write;
  dev.delay_ms = user_delay_ms;

  rslt = bme280_init(&dev);
  printf("\r\n BME280 Init Result is:%d \r\n",rslt);
  //stream_sensor_data_forced_mode(&dev);
  stream_sensor_data_normal_mode(&dev);
}


