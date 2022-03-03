#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN 9
#define CSN_PIN 10

const int max_payload_length = 32;
char char_buffer[max_payload_length];

// global flag to control flow of data from serial port
bool request_to_send = false;   // true = has data, false = no data

// global flag to control flow of data to serial port
bool clear_to_send = false;   // true = send it, false = no send

// Used to control whether this node is sending or receiving
bool role = false;  // true = TX role, false = RX role

const byte slaveAddress[6] = {'RxAAA'}; //must be the same on the receiver

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
    // receive data from serial interface
    // transmit data to transceiver
    // receive data from transceiver
}

//===============

void receive_from_serial()
{
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && new_data == false)
    {
        rc = Serial.read();

        if (recvInProgress == true)
        {
            if (rc != endMarker)
            {
                char_buffer[ndx] = rc;
                ndx++;
                if (ndx >= numChars)
                {
                    ndx = numChars - 1;
                }
            }
            else
            {
                char_buffer[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                new_data = true;
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
    if (clear_to_send == true)
    {
        Serial.print('<');
        Serial.print(char_buffer);
        Serial.print('>');
        // change the state of the LED everytime a reply is sent
        digitalWrite(ledPin, !digitalRead(ledPin));
        //new_data = false;
    }
}

//===============

void send_to_radio()
{
    unsigned char rc;

    if (request_to_send == false) {
        rc = -1;
    } 

    rc = radio.write(&char_buffer, sizeof(char_buffer));

    request_to_send = false;

    return rc;    
    
}
