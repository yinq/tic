#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"

//
// Hardware configuration
//

// Set up nRF24L01 radio on SPI bus plus pins 9 & 10

RF24 radio(9,10);

//
// Topology
//

// Radio pipe addresses for the 2 nodes to communicate.
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

//
// Role management
//
// Set up role.  This sketch uses the same software for all the nodes
// in this system.  Doing so greatly simplifies testing.  The hardware itself specifies
// which node it is.
//
// This is done through the role_pin
//

//
// Payload
//

const int relayPin = 8;
const int min_payload_size = 4;
const int max_payload_size = 32;
const int payload_size_increments_by = 2;
int next_payload_size = min_payload_size;

char receive_payload[max_payload_size+1]; // +1 to allow room for a terminating NULL char

void setup(void)
{
  pinMode(relayPin, OUTPUT);
  //
  // Print preamble
  //

  Serial.begin(57600);
  printf_begin();
  printf("\n\rRemote Switch\n\r");

  //
  // Setup and configure rf radio
  //

  radio.begin();

  // enable dynamic payloads
  radio.enableDynamicPayloads();

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(15,15);
  
  radio.setChannel(120);

  //
  // Open pipes to other nodes for communication
  //

  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1,pipes[0]);

  //
  // Start listening
  //

  radio.startListening();

  //
  // Dump the configuration of the rf unit for debugging
  //

  radio.printDetails();
}

void loop(void)
{
    // if there is data ready
    if ( radio.available() )
    {
      // Dump the payloads until we've gotten everything
      uint8_t len;
      bool done = false;
      while (!done)
      {
        // Fetch the payload, and see if this was the last one.
	len = radio.getDynamicPayloadSize();
	done = radio.read( receive_payload, len );

	// Put a zero at the end for easy printing
	receive_payload[len] = 0;

	// Spew it
	printf("Got payload size=%i value=%s\n\r",len,receive_payload);
        if (receive_payload[0] == '0') {
          printf("Off\n\r");
          digitalWrite(relayPin, LOW);
        } else {
          printf("On\n\r"); 
          digitalWrite(relayPin, HIGH);
        }
      }
      // Now, resume listening so we catch the next packets.
      radio.startListening();
    }
}
// vim:cin:ai:sts=2 sw=2 ft=cpp
