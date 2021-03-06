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
#include "RF24.h"
#include "printf.h"

/******************************************************************************************************
 * HARDWARE CONFIGURATION (USER INPUT REQUIRED)
 */
#define CE_PIN 9
#define CSN_PIN 10
bool radioNumber = 0;

/******************************************************************************************************
 * DEBUG CONFIGURATION (USER INPUT REQUIRED)
 */
bool DEBUG = false;

/******************************************************************************************************
 * CONTROL FLAGS
 */
// global flag to control flow of data from serial port
// true = received serial data, false = no new serial data
bool new_serial = false;

// global flag to control if the radio should respond to incoming receptions
// true = send ACK payloads, false = do not sent ACK payloads
bool send_ack = false;

// used to control the action that the transeiver will perform
// T=transmit, S=stream, R=receive (default)
char mode = 'R';

//used to control how many paylods must be streamed
uint32_t num_payloads = 0;

/******************************************************************************************************
 * GLOBAL DATA BUFFERS
 */
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
 * PAYLOAD STRUCT
 */
const uint16_t max_payload_length = 32;
struct PayloadStruct {
  char message[max_payload_length];
};
PayloadStruct payload;
PayloadStruct ackload;

/******************************************************************************************************
 * HEADER FRAME STRUCT
 */
#define num_substrings 3
char* header_frame[num_substrings];
char* header_mode;
char* header_payloads;
char* header_data;

/******************************************************************************************************
 * FUNCTION PROTOTYPES
 */
// serial functions
void init_serial(void);
void read_from_serial(void);
void send_to_serial(void);

// radio functions
void init_radio(void);
void get_radio_number(void);
void do_transmit(void);
void do_receive(void);
void do_stream(void);

// payload functions
void init_payload(void);
void make_header(void);
uint32_t get_num_payloads(void);
char get_mode(void);

// string functions
void slice(const char *str, char *result, size_t start, size_t end);
void split_buffer(char* str, char* dlm);
void copy(char* src, char* dst);

/******************************************************************************************************
 * @brief arduino main setup.
 * @returns void
 */
void setup() {
    init_serial();
    init_radio();
    init_payload();
    if (DEBUG) {
        Serial.println(F("Enter '<t:1:message>' to begin transmitting to the other radio!\n"));
    }
}

/******************************************************************************************************
 * @brief arduino main loop.
 * @returns void
 */
void loop() {
  receive_from_serial();
  if (new_serial){
    make_header();
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
    if (DEBUG) {
        Serial.println(F("\t\t***** Mock-Sat Half-Duplex Communication System *****"));
    }
    Serial.println(F("<ready: serial>"));
}

/******************************************************************************************************
 * @brief initialize the radio module.
 * @returns void
 */
void init_radio(){
    if (!radio.begin()) {
        Serial.println(F("<error: radio hardware is not responding>"));
        while (1) {} // hold in infinite loop
    }

    set_radio_number();
    radio.setPALevel(RF24_PA_LOW);  // RF24_PA_MAX is default.
    radio.enableDynamicPayloads();
    radio.enableAckPayload();
    radio.openWritingPipe(address[radioNumber]);
    radio.openReadingPipe(1, address[!radioNumber]);
    radio.startListening();

    if (DEBUG) {
        radio.printDetails();
    }

    Serial.print(F("<ready: "));
    Serial.print(F("radio"));
    Serial.print((int)radioNumber);
    Serial.println(F(">"));
}

/******************************************************************************************************
 * @brief initialize the global payload and the acknowledgement payload.
 * @returns void
 */
void init_payload(){
  // payload packet

  // acknowledgement packet
  memcpy(ackload.message, "ACK", 4);
  radio.writeAckPayload(1, &ackload, sizeof(PayloadStruct));
}

/******************************************************************************************************
 * @brief transmit a single payload to the other radio.
 * @note utilizes the global serial buffer.
 * @note should be setup by receiving a header serial message.
 * @returns void
 */
void do_transmit(){
    radio.flush_tx();
    unsigned long start_timer = micros();                             // start the timer
    slice(serial_buffer, payload.message, 0, max_payload_length);
    bool report = radio.write(&payload, sizeof(payload));             // transmit & save the report
    unsigned long end_timer = micros();                               // end the timer
    if (!report) {
        Serial.println(F("error: transmission failed or timed out")); // payload was not delivered
    } else {
        uint8_t pipe;
        if (!radio.available(&pipe)) {                                // expect to have an ACK packet... raise a warning if there is none!
            Serial.println(F("<warn: empty ACK packet>"));               // empty ACK packet received
        } else {
            PayloadStruct received;
            radio.read(&received, sizeof(received));                  // get incoming ACK payload
            if (DEBUG) {
                Serial.println(F("Transmission Report:"));            // print the timer result
                Serial.print(F("\t- Transmission Time: "));
                Serial.print(end_timer - start_timer);
                Serial.println(F(" us"));
                Serial.print(F("\t- Sent Message: "));
                Serial.println(payload.message);                      // print the outgoing message
                Serial.print(F("\t- Received Message: "));
                Serial.println(received.message);                     // print the incoming message
                Serial.print(F("\t- Extra Information: "));
                Serial.print(F("recieved "));
                Serial.print(radio.getDynamicPayloadSize());          // print incoming payload size
                Serial.print(F(" bytes on pipe "));
                Serial.println(pipe);
            } else {
                Serial.print(F("<"));
                Serial.print(received.message);
                Serial.print(F(">"));
            }
        }
    }
}

/******************************************************************************************************
 * @brief receive a payload from the other radio.
 * @returns void
 */
void do_receive(){
    uint8_t pipe;
    if (radio.available(&pipe)) {
        PayloadStruct received;
        radio.read(&received, sizeof(received));
        if (send_ack) {
            radio.writeAckPayload(1, &ackload, sizeof(PayloadStruct));  // send a manual acknowledgement package
        }
        if (DEBUG) {
            Serial.println(F("Reception Report:"));
            Serial.print(F("\t- Received Message: "));
            Serial.println(received.message);               // print incoming message
            Serial.print(F("\t- Response Message: "));
            Serial.println(ackload.message);                // print outgoing message
            Serial.print(F("\t- Extra Information: "));
            Serial.print(F("recieved "));
            Serial.print(radio.getDynamicPayloadSize());    // print incoming payload size
            Serial.print(F(" bytes on pipe "));
            Serial.println(pipe);
        } else {
            Serial.print(F("<"));
            Serial.print(received.message);
            Serial.println(F(">"));
        }
    }
}

/******************************************************************************************************
 * @brief stream payloads to the other radio.
 * @note utilizes the global serial buffer.
 * @note should be setup by receiving a header serial message, ex: <S:078:######>
 * @returns void
 */
void do_stream(){
    uint8_t i = 0;        // index variable for counting up to the required number of payloads sent
    uint8_t failures = 0; // radio transmits payload until too many errors occur

    slice(serial_buffer, payload.message, 0, max_payload_length);
    bool report = radio.write(&payload, sizeof(payload));

    radio.flush_tx();                       //  clean out the TX FIFO buffer
    radio.setPayloadSize(sizeof(payload));
    unsigned long start_timer = micros();

    while (i < num_payloads) {
        while (!new_serial){
            receive_from_serial();
        }
        new_serial = false;
        slice(serial_buffer, payload.message, 0, max_payload_length);
        if (DEBUG){
            Serial.print(F("sending: "));
            Serial.println(payload.message);
        }
        if (!radio.writeFast(&payload, sizeof(payload))) {
            failures++;
            radio.reUseTX();
        } else {
            i++;
        }
        if (failures >= 100) {
            Serial.print(F("<error: too many failures detected, aborting at payload: "));
            Serial.println(payload.message);
            Serial.print(F(" >"));
            break;
        }
    }
    unsigned long end_timer = micros();         // end the timer

    if (DEBUG){
        Serial.print(F("<time: "));
        Serial.print(end_timer - start_timer);      // print the timer result
        Serial.print(F(" us with "));
        Serial.print(failures);                     // print failures detected
        Serial.println(F(" failures detected>"));
    }
    // to make this example readable in the serial monitor
    delay(10);  // slow transmissions down by 10 millisecond
}

/******************************************************************************************************
 * @brief manually set the unique radio number for this radio. Number can be either 0 or 1. 
 * @returns void
 */
void set_radio_number(){
    if (DEBUG) {
        Serial.println(F("<enter radio number: '0' or '1'>"));
    }
    char input;
    while (!Serial.available()) {}  //wait for user inputs
    input = Serial.parseInt();
    radioNumber = input == 1;
}

/******************************************************************************************************
 * @brief gets the expected mode of the radio from the serial buffer. The mode character (R, S, T)
 * should always be the first character in the serial buffer when receiving a header message. 
 * @returns character representing mode (R (defualt), S, or T)
 */
char get_mode(){
  char rc = 'R';
  if (new_serial){
    rc = toupper(header_mode[0]);
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
  uint32_t n = (uint32_t) atoi(header_payloads);
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
 * |******************* HEADER FORMAT *********************|
 * < T/S/R  : NUM of EXPECTED TRANSMISSIONS  : EXTRA DATA >
 * |*******************************************************|
 */
void make_header(){
    if (new_serial){
        split_buffer(serial_buffer, ":");
        header_mode = header_frame[0];
        header_payloads = header_frame[1];
        header_data = header_frame[2];

        mode = get_mode();
        num_payloads = get_num_payloads();
        copy(header_data, serial_buffer);

        if (DEBUG){
            Serial.println(F("Received Header Frame!"));
            Serial.print(F("\t- mode: "));
            Serial.println(mode);
            Serial.print(F("\t- num payloads: "));
            Serial.println(num_payloads);
            Serial.print(F("\t- data: "));
            Serial.println(serial_buffer);
        }
    }
}

/******************************************************************************************************
 * @brief create a substring from str pointer and place into result pointer,
 *  incusive to both start and end character index.
 * @param   str     - pointer to the string to be sliced (source).
 * @param   dst     - pointer to the sub-string created from the slice (destination).
 * @param   start   - index of str that begins the slice (inclusive).
 * @param   end     - index of str that ends the slice (inclusive).
 * @returns void 
 */
void slice(const char *src, char *dst, size_t start, size_t end){
    strncpy(dst, src + start, end - start);
}

/******************************************************************************************************
 * @brief splits a string into multiple substrings seperated by the given deliminator.
 * @param   str   - the string to be split.
 * @param   dlm   - the string of a deliminator sequence
 * @returns void
 */
void split_buffer(char* str, char* dlm){
    char* text = strtok(str, dlm);
    uint8_t i = 0;
    while (text != 0 && i < num_substrings) {
        header_frame[i++] = text;
        text = strtok(0, dlm);
    }
}

/******************************************************************************************************
 * @brief copies the source string into the destination string.
 * @param   src   - the input string.
 * @param   dst   - the output string.
 * @returns void
 */
void copy(char* src, char* dst){
  memcpy(dst, src, strlen(src)+1);
}
