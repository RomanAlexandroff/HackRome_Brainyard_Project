/* ********************************************************************************************** */
/*                                                                                                */
/*   Flower Happiness Detector                                         :::::::::        :::       */
/*   globals.h                                                        :+:    :+:     :+: :+:      */
/*                                                                   +:+    +:+    +:+   +:+      */
/*   By: Roman Alexandrov <r.aleksandroff@gmail.com>                +#++:++#:    +#++:++#++:      */
/*                                                                 +#+    +#+   +#+     +#+       */
/*   Created: 2024/05/16 12:50:00                                 #+#    #+#   #+#     #+#        */
/*   Updated: 2024/05/16 18:45:00                                ###    ###   ###     ###         */
/*                                                                                                */
/* ********************************************************************************************** */

#ifndef GLOBALS_H_
# define GLOBALS_H_

# include <WiFi.h>
# include <WiFiMulti.h>
# include <ESPmDNS.h>                                           // for OTA
# include <WiFiUdp.h>                                           // for OTA
# include <ArduinoOTA.h>                                        // for OTA
# include <WiFiClientSecure.h>                                  // for Telegram
# include <UniversalTelegramBot.h>                              // for Telegram
# include "credentials.h"

extern WiFiMulti wifiMulti;
extern WiFiClientSecure secured_client;                         // for Telegram
extern UniversalTelegramBot bot;                                // for Telegram

struct rtc_global_variables {
    float    temp;
    uint16_t moisture;
    uint16_t battery;
    String   chat_id;
    String   from_name;
    uint8_t  last_notification;
    bool     ota;
    bool     reboot;
    uint8_t  hour;
    uint8_t  minute;
    uint8_t  day;
    uint8_t  month;
    uint16_t year;
};
extern struct rtc_global_variables rtc_g;

#endif
 
