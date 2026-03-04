#parameters.py

" parameter names and decsriptions"

param_names = [
    'HAP_ACT_INT',
    'HAP_AZIMUTH_MAX',
    'HAP_AZIMUTH_MIN',
    'HAP_DRV_EFFECT_B',
    'HAP_DRV_EFFECT_T',
    'HAP_ELEV_MAX',
    'HAP_ELEV_MIN',
    'HAP_MODE',
    'HAP_MULTIPLEX',
    'HAP_OFFSET_AVS_L',
    'HAP_OFFSET_AVS_R',
    'HAP_OFFSET_IMU',
    'HAP_PITCH_MAX',
    'HAP_PITCH_MIN',
    'HAP_Q_FACTOR',
    'HAP_ROLL_MAX',
    'HAP_ROLL_MIN',
    'HAP_SENSE_AVS_L',
    'HAP_SENSE_AVS_R',
    'HAP_SENSE_IMU',
    'HAP_TRIG_TIMER',
    'HAP_YAW_MAX',
    'HAP_YAW_MIN'
    ]

#param description
param_description = [
    '(active intensity)',
    '(maximum azimuth angle (AVS))',
    '(minimum azimuth angle (AVS))',
    '(bottom haptic waveform effect (1-123))',
    '(top haptic waveform effect (1-123))',
    '(maximum elevation angle (AVS))',
    '(minimum elevation angle (AVS))',
    '(haptic mode: IMU (0) or AVS (1))',
    '(using multiplexer, 1=enabled)',
    '(offset left AVS angle)',
    '(offset right AVS angle)',
    '(offset IMU angle)',
    '(maximum pitch angle (IMU))',
    '(minimum pitch angle (IMU))',
    '(q-factor)',
    '(maximum roll angle about x-axis (IMU))',
    '(minimum roll angle about x-axis (IMU))',
    '(sense left AVS (1 or -1))',
    '(sense right AVS (1 or -1))',
    '(sense IMU (1 or -1))',
    '(trigger timer)',
    '(maximum yaw angle (IMU))',
    '(minimum yaw angle (IMU))'
]