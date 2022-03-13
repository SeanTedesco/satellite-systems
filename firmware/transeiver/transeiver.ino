/******************************************************************************************************
 * INCLUDES
 */
#include <SPI.h>
#include "printf.h"
#include "RF24.h"

/******************************************************************************************************
 * HARDWARE CONFIGURATION
 */
#define CE_PIN 9
#define CSN_PIN 10

/******************************************************************************************************
 * CONTROL FLAGS
 */
// global flag to control flow of data from radio
// true = received payload data, false = no new payload data
bool new_payload = false;

// global flag to control flow of data to radio
// true = transmit payload data, false = no payload data to transmit
bool clear_for_radio = false;

// global flag to control flow of data from serial port
// true = received serial data, false = no new serial data
bool new_serial = false;

//global flag to control flow of data to serial port
// true = send data to serial port, false = no serial data to send
bool clear_for_serial = false;

// used to control the action that the transeiver will perform
// T=transmit, R=receive, S=stream, X=defualt
char mode = 'X';

/******************************************************************************************************
 * GLOBAL DATA BUFFERS
 */
const uint16_t max_payload_length = 32;
char payload_buffer[max_payload_length];

const uint16_t max_buffer_length = 512;
char serial_buffer[max_buffer_length];

char payload = 'a';
bool radioNumber = 1;

/******************************************************************************************************
 * RADIO PARAMETERS
 */
// Let these addresses be used for the pair
uint8_t address[][6] = {"1Node", "2Node"};

// instantiate an object for the nRF24L01 transceiver
RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

/******************************************************************************************************
 * ARDUINO SETUP
 */
void setup(){
  Serial.begin(115200);
  while (!Serial) {
  // some boards need to wait to ensure access to serial over USB
  }
  
  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("<error>"));
    Serial.println(F("<hardware not responding>"));
    while (1) {} // hold in infinite loop
  }

  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_LOW);
  radio.openWritingPipe(address[radioNumber]);
  radio.openReadingPipe(1, address[!radioNumber]);
  radio.stopListening();

  if (radioNumber) {
    radio.stopListening();  // put radio in TX mode
  } else {
    radio.startListening(); // put radio in RX mode
  }
  Serial.println("<ready>");
} 

/******************************************************************************************************
 * ARDUINO LOOP
 */
void loop(){
  if (Serial.available()) {
    // change the role via the serial input
    mode = toupper(Serial.read());
    if (mode == 'T'){
      // transmit data
      Serial.println(F("<ready transmit>"));
      radio.stopListening();
      do_transmit();

    } else if (mode == 'R' ){
      // receive data
      Serial.println(F("<ready receive>"));
      radio.startListening();
      do_receive();

    } else if (mode == 'S'){
      // stream data
      Serial.println(F("<ready stream>"));
      radio.stopListening();
      do_stream();
    } else {
      // listen for radio reception
      radio.startListening();
    }
  }
  Serial.println('.');
  delay(100);
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

bool send_to_serial(){
  bool rc = false;
  if (clear_for_serial){
    Serial.print('<');
    Serial.print(serial_buffer);
    Serial.print('>');
    new_serial = false;
    rc = true;
  }
  return rc;
}

//===============

bool send_to_radio(){
  bool rc = false;
  if (clear_for_radio == false) {
    return rc;
  } 
  rc = radio.write(&payload_buffer, sizeof(payload_buffer));
  clear_for_radio = false;
  return rc;
}

//===============

bool receive_from_radio(){
  bool rc = false;
  if (new_payload == true){
    return rc;
  }
  radio.read(&payload_buffer, sizeof(payload_buffer));
  new_payload = true;
  rc = true;
  return rc;
}

bool do_transmit(){
  bool rc = false;
  while(Serial.available()){Serial.read();}
  while(!Serial.available()){}
  payload = Serial.read();
  Serial.print("<sending: ");
  Serial.print(payload);
  Serial.println("> ");
  rc = radio.write(&payload, sizeof(payload));
  return rc;
}

bool do_receive(){
  bool rc = false; 
  uint8_t pipe;
  Serial.println("Press 'q' to quit");
  while (Serial.read() != 'q'){
    if (radio.available(&pipe)) {
      uint8_t bytes = radio.getPayloadSize();
      radio.read(&payload, bytes);
  
      Serial.print(F("Received "));
      Serial.print(bytes);                    // print the size of the payload
      Serial.print(F(" bytes on pipe "));
      Serial.print(pipe);                     // print the pipe number
      Serial.print(F(": "));
      Serial.println(payload);                // print the payload's value
    }
  }
  return rc;
}

bool do_stream()
{
    bool rc = false;
    return rc;
}
