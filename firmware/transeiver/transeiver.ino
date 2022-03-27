/*
 * Description: Firmware for serial controlled radio module. Used to send data to a sibling
 * radio. Default state is receiving, and can be manually controlled to transmit or stream data. 
 * 
 * Author: Sean Tedesco
 */
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
bool radioNumber = 0;

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

// global flag to control flow of data to serial port
// true = send data to serial port, false = no serial data to send
bool clear_for_serial = false;

// used to control the action that the transeiver will perform
// T=transmit, S=stream, R=receive (default)
char mode = 'R';

/******************************************************************************************************
 * GLOBAL DATA BUFFERS
 */
const uint16_t max_payload_length = 32;
char payload_buffer[max_payload_length];

const uint16_t max_buffer_length = 256;
char serial_buffer[max_buffer_length];

/******************************************************************************************************
 * RADIO PARAMETERS
 */
// Let these addresses be used for the pair
uint8_t address[][6] = {"1Node", "2Node"};

// instantiate an object for the nRF24L01 transceiver
RF24 radio(CE_PIN, CSN_PIN); // create a radio

/******************************************************************************************************
 * PAYLOAD PARAMETERS
 */
//float payload = 0.0;
struct PayloadStruct {
  char message[7];          // only using 6 characters for TX & ACK payloads
  uint8_t counter;
};
PayloadStruct payload;

/******************************************************************************************************
 * FUNCTION PROTOTYPES
 */
void init_serial(void);
void init_radio(void);
void get_radio_number(void);
void read_from_serial(void);
void do_transmit(void);
void do_receive(void);
char get_mode(void);
void print_serial_buffer(void);

/******************************************************************************************************
 * ARDUINO SETUP
 */
void setup() {
  init_serial();
  init_radio();

  memcpy(payload.message, "Hello ", 6);
  radio.writeAckPayload(1, &payload, sizeof(PayloadStruct));
  
  Serial.println(F("<enter '<t>' to begin transmitting to the other node>"));
}

/******************************************************************************************************
 * ARDUINO LOOP
 */
void loop() {
  mode = get_mode();
  if (mode == 'T'){
    //Serial.println(F("<changing to transmitter -- enter '<r>' to switch>"));
    radio.stopListening();
    do_transmit();
  } else if (mode == 'R'){
    //Serial.println(F("<changing to receiver -- enter '<t>' to switch>"));
    radio.startListening();
    do_receive();
  }
}

/******************************************************************************************************
 * INIT_SERIAL
 */
void init_serial(){
  Serial.begin(115200);
  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }
  Serial.println(F("<ready: serial>"));
}

/******************************************************************************************************
 * INIT_RADIO
 */
void init_radio(){
  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("<error: radio hardware is not responding>"));
    while (1) {} // hold in infinite loop
  }
  get_radio_number();
  radio.setPALevel(RF24_PA_LOW);  // RF24_PA_MAX is default.
  //radio.setPayloadSize(sizeof(payload)); 
  radio.enableDynamicPayloads();
  radio.enableAckPayload();
  radio.openWritingPipe(address[radioNumber]);
  radio.openReadingPipe(1, address[!radioNumber]);
  radio.startListening();
  Serial.println(F("<ready: radio>"));
}

/******************************************************************************************************
 * GET_RADIO_NUMBER
 */
void get_radio_number(){
  char input;
  Serial.println(F("<enter radio number: '0' or '1'>"));
  while (!Serial.available()) {
    // wait for user inputs
  }
  input = Serial.parseInt();
  radioNumber = input == 1;
  Serial.print(F("<radioNumber = "));
  Serial.print((int)radioNumber);
  Serial.println(F(">"));
}


/******************************************************************************************************
 * DO_TRANSMIT
 */
void do_transmit() {
    unsigned long start_timer = micros();                    // start the timer
    bool report = radio.write(&payload, sizeof(payload));    // transmit & save the report
    unsigned long end_timer = micros();                      // end the timer

    if (report) {
      Serial.print(F("Transmission successful! "));          // payload was delivered
      Serial.print(F("Time to transmit = "));
      Serial.print(end_timer - start_timer);                 // print the timer result
      Serial.print(F(" us. Sent: "));
      Serial.print(payload.message);                         // print the outgoing message
      Serial.print(payload.counter);                         // print the outgoing counter
      uint8_t pipe;
      if (radio.available(&pipe)) {                          // is there an ACK payload? grab the pipe number that received it
        PayloadStruct received;
        radio.read(&received, sizeof(received));             // get incoming ACK payload
        Serial.print(F(" Recieved "));
        Serial.print(radio.getDynamicPayloadSize());         // print incoming payload size
        Serial.print(F(" bytes on pipe "));
        Serial.print(pipe);                                  // print pipe number that received the ACK
        Serial.print(F(": "));
        Serial.print(received.message);                      // print incoming message
        Serial.println(received.counter);                    // print incoming counter

        // save incoming counter & increment for next outgoing
        payload.counter = received.counter + 1;

      } else {
        Serial.println(F(" Recieved: an empty ACK packet")); // empty ACK packet received
      }


    } else {
      Serial.println(F("Transmission failed or timed out"));    // payload was not delivered
    }

    // to make this example readable in the serial monitor
    delay(1000);  // slow transmissions down by 1 second
}

/******************************************************************************************************
 * DO_RECEIVE
 */
void do_receive() {
    uint8_t pipe;
    if (radio.available(&pipe)) {                    // is there a payload? get the pipe number that recieved it
      uint8_t bytes = radio.getDynamicPayloadSize(); // get the size of the payload
      PayloadStruct received;
      radio.read(&received, sizeof(received));       // get incoming payload
      Serial.print(F("Received "));
      Serial.print(bytes);                           // print the size of the payload
      Serial.print(F(" bytes on pipe "));
      Serial.print(pipe);                            // print the pipe number
      Serial.print(F(": "));
      Serial.print(received.message);                // print incoming message
      Serial.print(received.counter);                // print incoming counter
      Serial.print(F(" Sent: "));
      Serial.print(payload.message);                 // print outgoing message
      Serial.println(payload.counter);               // print outgoing counter

      // save incoming counter & increment for next outgoing
      payload.counter = received.counter + 1;
      // load the payload for the first received transmission on pipe 0
      radio.writeAckPayload(1, &payload, sizeof(payload));
    }
  delay(10);
}

/******************************************************************************************************
 * READ_FROM_SERIAL
 */
char get_mode(){
  char rc = 'R';
  if (Serial.available()) {
    receive_from_serial();
    if (new_serial){
      rc = toupper(serial_buffer[0]);
      new_serial = false;
    }
  }
  return rc;
}

/******************************************************************************************************
 * RECEIVE_FROM_SERIAL
 */
void receive_from_serial(){
  static bool recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && new_serial == false){
    rc = Serial.read();
    if (recvInProgress == true){
      if (rc != endMarker){
        serial_buffer[ndx] = rc;
        ndx++;
        if (ndx >= max_buffer_length){
          ndx = max_buffer_length - 1;
        }
      } else{
        serial_buffer[ndx] = '\0';
        recvInProgress = false;
        ndx = 0;
        new_serial = true;
        //print_serial_buffer();
      }
    }else if (rc == startMarker){
      recvInProgress = true;
    }
  }
}

/******************************************************************************************************
 * PRINT_SERIAL_BUFFER
 */
void print_serial_buffer(){
  Serial.print(F("<serial buffer: "));
  Serial.print(serial_buffer);
  Serial.println(F(">"));
}
