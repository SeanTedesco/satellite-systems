#include <SPI.h>
#include "printf.h"
#include "RF24.h"

#define CE_PIN 9
#define CSN_PIN 10

const int max_payload_length = 32;
char payload_buffer[max_payload_length];

const int max_buffer_length = 512;
char serial_buffer[max_buffer_length];

// global flag to control flow of data from radio
bool new_payload = false;       // true = received payload data, false = no new payload data

// global flag to control flow of data to radio
bool clear_for_radio = false;   // true = transmit payload data, false = no payload data to transmit

// global flag to control flow of data from serial port
bool new_serial = false;        // true = received serial data, false = no new serial data

//global flag to control flow of data to serial port
bool clear_for_serial = false;  // true = send data to serial port, false = no serial data to send 

// used to control the action that the transeiver will perform
char mode; // T=transmit, R=receive, S=stream

const byte slaveAddress[6] = {'RxTxA'}; //must be the same on the receiver

RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

//===============

void setup()
{
    Serial.begin(115200);

    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);
    delay(200);
    digitalWrite(ledPin, LOW);
    delay(200);
    digitalWrite(ledPin, HIGH);

    radio.begin();
    radio.setDataRate(RF24_250KBPS);
    radio.setRetries(3, 5); // delay, count
    radio.openWritingPipe(slaveAddress);
    radio.stopListening();

    Serial.println("<ready>");
}

//===============

void loop()
{
    if (Serial.available()) {
    // change the role via the serial input

        mode = receive_from_serial();
        if (!strcmp("<T>", mode) && !role) {
            // transmit data
            role = true;
            Serial.println(F("<ready>"));
            radio.stopListening();
            do_transmit();

        } else if (!strcmp("<R>", mode) && role) {
            // receive data
            role = false;
            Serial.println(F("<ready>"));
            radio.startListening();
            do_receive();

        } else if (!strcmp("<S>", mode) && !role){
            // stream data
            role = true;
            Serial.println(F("<ready>"));
            radio.stopListening();
            do_stream();
        } else {
            // listen for radio reception
            role = false
            radio.startListening();
        }
    }
}

//===============

void receive_from_serial()
{
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && new_serial == false)
    {
        rc = Serial.read();

        if (recvInProgress == true)
        {
            if (rc != endMarker)
            {
                serial_buffer[ndx] = rc;
                ndx++;
                if (ndx >= max_buffer_length)
                {
                    ndx = max_buffer_length - 1;
                }
            }
            else
            {
                serial_buffer[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                new_serial = true;
            }
        }

        else if (rc == startMarker)
        {
            recvInProgress = true;
        }
    }
}

//===============

void send_to_serial()
{
    unsigned char rc = 0;

    if (clear_for_serial){
        Serial.print('<');
        Serial.print(serial_buffer);
        Serial.print('>');
        // change the state of the LED everytime a reply is sent
        digitalWrite(ledPin, !digitalRead(ledPin));
        new_serial = false;
    } else {
        rc = -1;
    } 

}

//===============

void send_to_radio()
{
    unsigned char rc;

    if (clear_to_send == false) {
        rc = -1;
        return rc;
    } 

    rc = radio.write(&payload_buffer, sizeof(payload_buffer));

    clear_to_send = false;

    return rc;    
    
}

//===============

void receive_from_radio()
{
    unsigned char rc;

    if (new_payload == true) {
        rc = -1;
        return rc;
    }

    rc = radio.read(&payload_buffer, sizeof(payload_buffer));

    new_payload = true;

    return rc;
}

void do_transmit()
{
    unsigned char rc = 0;
    return rc;
}

void do_receive()
{
    unsigned char rc = 0;
    return rc;
}

void do_stream()
{
    unsigned char rc = 0;
    return rc;
}