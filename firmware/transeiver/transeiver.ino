/*
 * Description: Firmware for serial controlled radio module. Used to send data to a sibling
 * radio. Default state is receiving, and can be manually controlled to transmit or stream data. 
 * 
 * Easy setup is made with the RF24 protoboard found in the hardware files of `satellite-systems`
 * repository. 
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
 * HARDWARE CONFIGURATION (USER INPUT REQUIRED)
 */
#define CE_PIN 9
#define CSN_PIN 10
bool radioNumber = 0;

/******************************************************************************************************
 * DEBUG CONFIGURATION (USER INPUT REQUIRED)
 */
bool DEBUG = true;

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
const uint16_t max_payload_length = 29;
char payload_buffer[max_payload_length + 1];

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
  char message[29];
  uint8_t counter;
};
PayloadStruct payload;

/******************************************************************************************************
 * FUNCTION PROTOTYPES
 */
void init_serial(void);
void read_from_serial(void);
void send_to_serial(void);

void init_radio(void);
void get_radio_number(void);
void do_transmit(void);
void do_receive(void);
void do_stream(void);

void init_payload(void);
void make_header(void);
uint32_t get_num_payloads(void);
char get_mode(void);

void slice(const char *str, char *result, size_t start, size_t end);

/******************************************************************************************************
 * @brief arduino main setup.
 * @returns void
 */
void setup() {
  init_serial();
  init_radio();
  init_payload();
  Serial.println(F("<enter '<t>' to begin transmitting to the other node>"));
}

/******************************************************************************************************
 * @brief arduino main loop.
 * @returns void
 */
void loop() {
  receive_from_serial();
  if (new_serial){
    mode = get_mode();
    new_serial = false;
  }
  if (mode == 'T'){
    radio.stopListening();
    do_transmit();
    mode = 'R';
  } else if (mode == 'S'){
    radio.stopListening();
    do_stream();
    mode = 'R';
  } else if (mode == 'R'){
    radio.startListening();
    do_receive();
  } else {
    Serial.print(F("<error: unknown mode: "));
    Serial.print(mode);
    Serial.println(F(">"));
    mode = 'R';
  }
}

/******************************************************************************************************
 * @brief initialize the serial module.
 * @returns void
 */
void init_serial(){
  Serial.begin(115200);
  while (!Serial) {} // some boards need to wait to ensure access to serial over USB
  Serial.println(F("<ready: serial>"));
}

/******************************************************************************************************
 * @brief initialize the radio module.
 * @returns void
 */
void init_radio(){
  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("<error: radio hardware is not responding>"));
    while (1) {} // hold in infinite loop
  }
  if (DEBUG){
    set_radio_number();
  }
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
 * @brief initialize the global payload and the acknowledgement payload.
 * @returns void
 */
void init_payload(){
  payload_buffer[max_payload_length] = 0;
  memcpy(payload.message, "Hello ", 6);
  radio.writeAckPayload(1, &payload, sizeof(PayloadStruct));
}

/******************************************************************************************************
 * @brief manually set the unique radio number for this radio. Number can be either 0 or 1. 
 * @returns void
 */
void set_radio_number(){
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
 * @brief transmit a single payload to the other radio.
 * @note utilizes the global serial buffer.
 * @note should be setup by receiving a header serial message.
 * @returns void
 */
void do_transmit(){
  radio.flush_tx();
  unsigned long start_timer = micros();                    // start the timer
  slice(serial_buffer, payload.message, 1, max_payload_length);
  bool report = radio.write(&payload, sizeof(payload));    // transmit & save the report
  unsigned long end_timer = micros();                      // end the timer

  if (report) {
    if (DEBUG) {
      Serial.print(F("Transmission successful! "));          // payload was delivered
      Serial.print(F("Time to transmit = "));
      Serial.print(end_timer - start_timer);                 // print the timer result
      Serial.print(F(" us. Sent: "));
      Serial.print(payload.message);                         // print the outgoing message
      Serial.print(payload.counter);                         // print the outgoing counter
    } else {
      memcpy(serial_buffer, payload.message, max_payload_length);
      send_to_serial();
    }

    uint8_t pipe;
    if (radio.available(&pipe)) {                             // is there an ACK payload? grab the pipe number that received it
      PayloadStruct received;
      radio.read(&received, sizeof(received));                // get incoming ACK payload
      if (DEBUG) {
        Serial.print(F(" Recieved "));
        Serial.print(radio.getDynamicPayloadSize());          // print incoming payload size
        Serial.print(F(" bytes on pipe "));
        Serial.print(pipe);                                   // print pipe number that received the ACK
        Serial.print(F(": "));
        Serial.print(received.message);                       // print incoming message
        Serial.println(received.counter);                     // print incoming counter
        payload.counter = received.counter + 1;
      }

    } else {
      Serial.println(F("warn: an empty ACK packet"));    // empty ACK packet received
    }
  } else {
    Serial.println(F("error: transmission failed or timed out"));    // payload was not delivered
  }

    // to make this example readable in the serial monitor
    delay(10);  // slow transmissions down by 10 millisecond
}

/******************************************************************************************************
 * @brief receive a payload from the other radio.
 * @note utilizes the global serial buffer.
 * @note should be setup by receiving a header serial message.
 * @returns void
 */
void do_receive(){
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
 * @brief stream payloads to the other radio.
 * @note utilizes the global serial buffer.
 * @note should be setup by receiving a header serial message, ex: <s078######>
 * @returns void
 */
void do_stream(){

  uint8_t i = 0;
  uint8_t failures = 0;
  uint32_t num_payloads = get_num_payloads();

  radio.flush_tx();
  radio.setPayloadSize(sizeof(payload));
  unsigned long start_timer = micros();
  while (i < num_payloads) {
    while (!new_serial){
      receive_from_serial();
    }
    slice(serial_buffer, payload.message, 0, max_payload_length);
    if (!radio.writeFast(&payload, sizeof(payload))) {
      failures++;
      radio.reUseTX();
    } else {
      i++;
    }
    if (failures >= 100) {
      Serial.print(F("error: too many failures detected. Aborting at payload "));
      Serial.println(payload.message);
      break;
    }
  }
  unsigned long end_timer = micros();         // end the timer

  if (DEBUG){
    Serial.print(F("Time to transmit = "));
    Serial.print(end_timer - start_timer);      // print the timer result
    Serial.print(F(" us with "));
    Serial.print(failures);                     // print failures detected
    Serial.println(F(" failures detected"));
  }
  // to make this example readable in the serial monitor
  delay(10);  // slow transmissions down by 10 millisecond
}

/******************************************************************************************************
 * @brief gets the expected mode of the radio from the serial buffer. The mode character (R, S, T)
 * should always be the first character in the serial buffer when receiving a header message. 
 * @returns character representing mode (R (defualt), S, or T)
 */
char get_mode(){
  char rc = 'R';
  if (new_serial){
    rc = toupper(serial_buffer[0]);
  }
  return rc;
}

/******************************************************************************************************
 * @brief receive a message from the serial port. This is the main way the "radio" interfaces
 * with the outside world. Serial communication is indicated with both start and end markers.
 * @note populates the global serial buffer
 * @returns void
 */
void receive_from_serial(){
  static bool recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;
  
  if (Serial.available()) {
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
        }
      } else if (rc == startMarker){
        recvInProgress = true;
      }
    }
  }
}

/******************************************************************************************************
 * @brief send the contents of the global serial buffer to the serial port.
 * @returns void
 */
void send_to_serial(){
  Serial.print(F("<"));
  Serial.print(serial_buffer);
  Serial.println(F(">"));
}

/******************************************************************************************************
 * @brief provide the number of 
 * @note should be called when starting a transmission and after 
 * successfully receiving the first serial message.
 * @returns the number of payloads (30 bytes) to be sent. 
 */
uint32_t get_num_payloads(){
  uint16_t n = atoi(serial_buffer[1]);
  uint16_t d;
  for (uint8_t i=1; i<4; i++){
    d = atoi(serial_buffer[i]);
    n = n*10 + d
  }
  return n;
}

/******************************************************************************************************
 * @brief copies the first 30 bytes of the serial buffer into the payload
 * message buffer.
 * @note should be called after successfully receiving a serial
 * message.
 * @note should be used as the first message between radios to set
 * configurations (such as modes).
 * @returns void
 * 
 * |***         HEADER FORMAT (30 BYTES)        ***|
 * |   1    |         2-4             |   5-30     |
 * | T/S/R  | EXPECTED TRANSMISSIONS  | EXTRA DATA |
 */
void make_header(){
  if (new_serial){
    mode = get_mode();
    num_payloads = get_num_payloads();
    slice(serial_buffer, payload.message, 4, max_payload_length);
  }
}

/******************************************************************************************************
 * @brief create a substring from str pointer and place into result pointer,
 *  incusive to both start and end character index.
 * @param str - pointer to the string to be sliced.
 * @param result - pointer to the sub-string created from the slice.
 * @param start - index of str that begins the slice (inclusive).
 * @param end - index of str that ends the slivce (inclusive).
 * @returns void 
 */
void slice(const char *str, char *result, size_t start, size_t end){
    strncpy(result, str + start, end - start);
}
