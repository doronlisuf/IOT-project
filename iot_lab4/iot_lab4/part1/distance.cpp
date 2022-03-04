#include <wiringPi.h>

#define TRIG 17
#define ECHO 27

// Initialize wiringPi and allow the use of GPIO pin numbering
wiringPiSetupGpio();

// Setup the ECHO pin as input and TRIG as output
pinMode(TRIG, OUTPUT);
pinMode(ECHO, INPUT);

// set the TRIG pin to low
digitalWrite(TRIG, LOW);

// wait for 2 ms
delay(2);

// set the TRIG pin to high
digitalWrite(TRIG, HIGH);

// delay for 0.1 ms
delay(0.1);

// set the TRIG pin to low
digitalWrite(TRIG, LOW);

// instantiate time variables
unsigned int start_time;
unsigned int end_time;

// save start_time while ECHO is low
while(digitalRead(ECHO) == LOW)
    start_time = micros();

// save end_time while ECHO is high
while(digitalRead(ECHO) == HIGH)
    end_time = micros();

// calculate duration
unsigned int dur = end_time - start_time;

// set output to distance
Output = (int)(dur / 58.2);