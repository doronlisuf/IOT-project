#include <wiringPi.h>

#define BUTTON 14
#define LED 2

// Initialize wiringPi and allow the use of GPIO pin numbering
wiringPiSetupGpio();

// Setup the BUTTON pin as input and LED as output
pinMode(BUTTON, INPUT);
pinMode(LED, OUTPUT);

// wait for button to be pressed
while(1)
{
    if(digitalRead(BUTTON) == HIGH)
    {
        // delay for debouncing purposes
        delay(500);

        // turn LED on
        digitalWrite(LED, HIGH);

        // delay for half a second
        delay(500);

        // detect button release
        if(digitalRead(BUTTON) == LOW)
        {
            break;
        }
    }
}

// turn led off
digitalWrite(LED, LOW);