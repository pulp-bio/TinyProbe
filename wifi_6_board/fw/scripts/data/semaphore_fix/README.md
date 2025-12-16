# Semaphore Fix Data

## Measurements 15.12.2025

Digital channels:

- CH0: CLK
- CH1: MOSI
- CH2: MISO
- CH3: CS
- CH4: INT

Use [`plot_scope_bin.ipynb`](../../plot_scope_bin.ipynb) to visualize the data.

- `_singleshot`: 400 MSa/s, single shot acquisition
- `_multishot`: 200 MSa/s, 5 shots acquisition

## Measurements 16.12.2025

100 MSa/s

`config_1.json`:

- `tp_1.bin`/`tp_3.bin`/`tp_5.bin`: Successful
- `tp_2.bin`/`tp_4.bin`: WriteFPGA failed
  
  ```log
  Received command sequence of length 108
  [ERR]   Expected 0x00000010, got 0x00000000
  [ERR]   Error at C:/dev/Tinyprobe/wifi_6_board/fw/user/tp/commands/tp_command_writefpga.c:46: 0x1
  [ERR]   Command 4 failed with status 0x1
  [ERR]     -> Reason: SL_STATUS_FAIL
  [INF]   Triggering 1 shots with 1 packets each
  [INF]   Done
  ```

  ```bash
                           Device Responses
  ┏━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
  ┃ IDX ┃ Cmd. ID ┃ Status ┃ Data ┃ Error ┃ Resp. Time ┃ Exec. Time ┃
  ┡━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
  │   5 │       4 │ ERROR  │      │     1 │     6.6 ms │     0.0 ms │
  └─────┴─────────┴────────┴──────┴───────┴────────────┴────────────┘
  ```

`config_2.json`:

- `tp_6.bin`/`tp_7.bin`/`tp_9.bin`: Successful
- `tp_8.bin`: WriteFPGA failed
  
  ```log
  Received command sequence of length 108
  [ERR]   Expected 0x00000010, got 0x00000000
  [ERR]   Error at C:/dev/Tinyprobe/wifi_6_board/fw/user/tp/commands/tp_command_writefpga.c:46: 0x1
  [ERR]   Command 4 failed with status 0x1
  [ERR]     -> Reason: SL_STATUS_FAIL
  [INF]   Triggering 1 shots with 3 packets each
  [INF]   Done
  ```

  ```bash
                           Device Responses
  ┏━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
  ┃ IDX ┃ Cmd. ID ┃ Status ┃ Data ┃ Error ┃ Resp. Time ┃ Exec. Time ┃
  ┡━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
  │   5 │       4 │ ERROR  │      │     1 │     6.6 ms │     0.0 ms │
  └─────┴─────────┴────────┴──────┴───────┴────────────┴────────────┘
  ```

`config_3.json`:

- `tp_10.bin`/`tp_11.bin`: Successful

`config_4.json`:

- `tp_12.bin`/`tp_15.bin`: Successful
- `tp_13.bin`/`tp_14.bin`: WriteFPGA failed
  
  ```log
  Received command sequence of length 108
  [ERR]   Expected 0x00000010, got 0x00000000
  [ERR]   Error at C:/dev/Tinyprobe/wifi_6_board/fw/user/tp/commands/tp_command_writefpga.c:46: 0x1
  [ERR]   Command 4 failed with status 0x1
  [ERR]     -> Reason: SL_STATUS_FAIL
  [INF]   Triggering 5 shots with 3 packets each
  [INF]   Done
  ```

  ```bash
                           Device Responses
  ┏━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
  ┃ IDX ┃ Cmd. ID ┃ Status ┃ Data ┃ Error ┃ Resp. Time ┃ Exec. Time ┃
  ┡━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
  │   5 │       4 │ ERROR  │      │     1 │     6.6 ms │     0.0 ms │
  └─────┴─────────┴────────┴──────┴───────┴────────────┴────────────┘
  ```

`config_5.json`:

- `tp_16.bin`/`tp_17.bin`: WriteFPGA failed
  
  ```log
  Received command sequence of length 108
  [ERR]   Expected 0x00000010, got 0x00000000
  [ERR]   Error at C:/dev/Tinyprobe/wifi_6_board/fw/user/tp/commands/tp_command_writefpga.c:46: 0x1
  [ERR]   Command 4 failed with status 0x1
  [ERR]     -> Reason: SL_STATUS_FAIL
  [INF]   Triggering 5 shots with 16 packets each
  [INF]   Done
  ```

  ```bash
                           Device Responses
  ┏━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
  ┃ IDX ┃ Cmd. ID ┃ Status ┃ Data ┃ Error ┃ Resp. Time ┃ Exec. Time ┃
  ┡━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
  │   5 │       4 │ ERROR  │      │     1 │     6.6 ms │     0.0 ms │
  └─────┴─────────┴────────┴──────┴───────┴────────────┴────────────┘
  ```

`config_6.json`:

- `tp_18.bin`: WriteFPGA failed and one FIFO ready flag missed
  
  ```log
  Received command sequence of length 108
  [ERR]   Expected 0x00000010, got 0x00000000
  [ERR]   Error at C:/dev/Tinyprobe/wifi_6_board/fw/user/tp/commands/tp_command_writefpga.c:46: 0x1
  [ERR]   Command 4 failed with status 0x1
  [ERR]     -> Reason: SL_STATUS_FAIL
  [INF]   Triggering 5 shots with 41 packets each
  [ERR]   Error waiting for FIFO data ready flag
  [INF]   Done
  ```

  ```bash
                           Device Responses
  ┏━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
  ┃ IDX ┃ Cmd. ID ┃ Status ┃ Data ┃ Error ┃ Resp. Time ┃ Exec. Time ┃
  ┡━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
  │   5 │       4 │ ERROR  │      │     1 │     6.6 ms │     0.0 ms │
  └─────┴─────────┴────────┴──────┴───────┴────────────┴────────────┘
  ```
- `tp_19.bin`: One FIFO ready flag missed
  
  ```log
  [INF]   Received command sequence of length 108
  [INF]   Triggering 5 shots with 41 packets each
  [ERR]   Error waiting for FIFO data ready flag
  [INF]   Done
  ```

