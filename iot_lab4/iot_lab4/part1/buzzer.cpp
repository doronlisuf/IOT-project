#include <wiringPi.h>

#define BUZZER 4 

// Initialize wiringPi and allow the use of GPIO pin numbering
wiringPiSetupGpio();

// Setup the BUZZER pin as output
pinMode(BUZZER, OUTPUT);

// loop through 5 iterations of buzzer activation
for(int i=0; i<5; i++)
{
    // turn buzzer on
    digitalWrite(BUZZER, HIGH);

    // wait for half a second
    delay(500);

    // turn buzzer off
    digitalWrite(BUZZER, LOW);

    // wait for half a second
    delay(500);
}

// ensure buzzer is off
digitalWrite(BUZZER, LOW);