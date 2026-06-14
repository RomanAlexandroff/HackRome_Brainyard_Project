
/* ********************************************************************************************** */
/*                                                                                                */
/*   Flower Happiness Detector                                         :::::::::        :::       */
/*   post_to_database.cpp                                             :+:    :+:     :+: :+:      */
/*                                                                   +:+    +:+    +:+   +:+      */
/*   By: Roman Alexandrov <r.aleksandroff@gmail.com>                +#++:++#:    +#++:++#++:      */
/*                                                                 +#+    +#+   +#+     +#+       */
/*   Created: 2026/06/13 16:30:00                                 #+#    #+#   #+#     #+#        */
/*   Updated: 2026/06/13 16:45:00                                ###    ###   ###     ###         */
/*                                                                                                */
/* ********************************************************************************************** */

#include "Flower_Happiness_Detector.h"
#include <HTTPClient.h>

static void build_json_payload(char *buffer, size_t size)
{
    snprintf(
        buffer,
        size,
        "{\"temperature\":%.2f,\"moisture\":%d,\"battery\":%d}",
        rtc_g.temp,
        rtc_g.moisture,
        rtc_g.battery
    );
}

int8_t post_to_database(void)
{
    HTTPClient http;
    char payload[128];
    int response_code;

    if (WiFi.status() != WL_CONNECTED)
    {
        DEBUG_PRINTF("\n[DATABASE] Wi-Fi not connected");
        return (0);
    }
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Gateway: ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("Subnet: ");
    Serial.println(WiFi.subnetMask());
    build_json_payload(payload, sizeof(payload));
    DEBUG_PRINTF("\n[DATABASE] Connecting to backend...");
    http.begin("http://172.20.10.4:8000/sensor");
    http.addHeader("Content-Type", "application/json");
    response_code = http.POST(payload);
    DEBUG_PRINTF("\n[DATABASE] Payload: %s", payload);
    DEBUG_PRINTF("\n[DATABASE] Response code: %d", response_code);
    if (response_code > 0)
    {
        String response = http.getString();
        DEBUG_PRINTF(
            "\n[DATABASE] Server response: %s",
            response.c_str()
        );
        http.end();
        return (1);
    }
    DEBUG_PRINTF("\n[DATABASE] POST failed");
    http.end();
    return (0);
}
