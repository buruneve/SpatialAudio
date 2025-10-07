#include <Wire.h>
#include <Adafruit_DRV2605.h>

Adafruit_DRV2605 drv;

#define TCAADDR 0x70  // I2C address of TCA9548A

void tcaSelect(uint8_t channel) {
  if (channel > 2) return;
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << channel);
  Wire.endTransmission();
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  // Serial.println("Haptic Feedback Controller Ready");

  // Initialize both haptic drivers through the multiplexer
  for (uint8_t i = 0; i < 2; i++) {
    tcaSelect(i);
    if (!drv.begin()) {
      Serial.print("DRV2605 on channel ");
      Serial.print(i);
      Serial.println(" not found!");
    } else {
      drv.selectLibrary(1);
      drv.setMode(DRV2605_MODE_INTTRIG);
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    // Serial.print("Received command: ");
    // Serial.println(cmd);

    if (cmd == 'A') {
      // Right motor (channel 0)
      triggerHaptic(0);
    } 
    else if (cmd == 'B') {
      // Left motor (channel 1)
      triggerHaptic(1);
    }
  }
}

void triggerHaptic(uint8_t channel) {
  tcaSelect(channel);
  drv.setWaveform(0, 47);  // Strong click (preset)
  drv.setWaveform(1, 0);   // End of sequence
  drv.go();

  // Serial.print("Triggered haptic on channel ");
  // Serial.println(channel);
}

