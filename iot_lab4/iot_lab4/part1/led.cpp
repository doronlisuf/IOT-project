#include <wiringPi.h>

#define LED 2

// Initialize wiringPi and allow the use of GPIO pin numbering
wiringPiSetupGpio();

// Setup the LED pin as output
pinMode(LED, OUTPUT);

// loop through 5 iterations of LED activation
for(int i=0; i<5; i++) 
{
    // turn LED on
    digitalWrite(LED, HIGH);

    // wait for half a second
    delay(500);
    
    // turn LED off
    digitalWrite(LED, LOW);

    // wait for half a second
    delay(500);
} 

// ensure LED is off
digitalWrite(LED, LOW);