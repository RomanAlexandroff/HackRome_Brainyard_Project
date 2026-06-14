/* ********************************************************************************************** */
/*                                                                                                */
/*   Flower Happiness Detector                                         :::::::::        :::       */
/*   temperature.cpp                                                  :+:    :+:     :+: :+:      */
/*                                                                   +:+    +:+    +:+   +:+      */
/*   By: Roman Alexandrov <r.aleksandroff@gmail.com>                +#++:++#:    +#++:++#++:      */
/*                                                                 +#+    +#+   +#+     +#+       */
/*   Created: 2024/05/22 12:50:00                                 #+#    #+#   #+#     #+#        */
/*   Updated: 2024/05/22 18:45:00                                ###    ###   ###     ###         */
/*                                                                                                */
/* ********************************************************************************************** */

#include "Flower_Happiness_Detector.h"

static temperature_sensor_handle_t temp_handle;

static void temperature_calibration(void)
{
    int8_t  i;
    float   temperature;

    i = 0;
    temperature_sensor_get_celsius(temp_handle, &temperature);
    while (temperature > 130.00 && i < 20)
    {
        temperature_sensor_get_celsius(temp_handle, &temperature);
        delay(500);
        i++;
        DEBUG_PRINTF("\n[TEMPERATURE SENSOR] Temperature calibration in process, iteration #%d", i);
    }
}

void  temperature_check(void)
{
    int8_t  i;
    float   total;
    float   temperature;

    i = 0;
    total = 0;
    temperature = 0;
    temperature_calibration();
    while (i < 5)
    {
        temperature_sensor_get_celsius(temp_handle, &temperature);
        total += temperature;
        delay(500);
        i++;
    }
    rtc_g.temp = total / i;
    DEBUG_PRINTF("\n[TEMPERATURE SENSOR] Current temperature: %.2f°C\n", rtc_g.temp);
}

void temp_sensor_init(void)
{
    temperature_sensor_config_t cfg = TEMPERATURE_SENSOR_CONFIG_DEFAULT(10, 80);
    temperature_sensor_install(&cfg, &temp_handle);
}
 
