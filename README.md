# MacKavserCAN

Mac 용 Kvaser CAN 인터페이스를 위한 Python 클래스 래퍼입니다. 이 라이브러리는 [mac-can/KvaserCAN-Library](https://github.com/mac-can/KvaserCAN-Library)의 Python 래퍼를 기반으로 객체지향적인 인터페이스를 제공합니다.

## 주요 기능

- 사용 가능한 CAN 채널 자동 탐지
- CAN 메시지 송수신 (표준 및 확장 ID 지원)
- CAN 버스 모니터링
- CAN 인터페이스 상태 확인
- 비트레이트 설정 및 정보 확인
- 버스 부하 모니터링
- 콜백 기반 메시지 처리

## 설치 요구사항

- Python 3.6 이상
- macOS 환경 (Linux, Windows에서도 라이브러리 경로 수정 후 사용 가능)
- Kvaser CAN 디바이스
- KvaserCAN-Library (libUVCANKVL.dylib)

## 설치 방법

1. [mac-can/KvaserCAN-Library](https://github.com/mac-can/KvaserCAN-Library) 저장소 클론:
   ```bash
   git clone https://github.com/mac-can/KvaserCAN-Library.git
   ```

2. KvaserCAN-Library 빌드 및 설치:
   ```bash
   cd KvaserCAN-Library
   ./build_no.sh
   make all
   sudo make install
   ```
3. 설치 확인
   ```bash
   # 빌드 후 생성된 라이브러리 파일을 수동으로 복사해줍니다
   sudo cp Libraries/KvaserCAN/libKvaserCAN.0.3.4.dylib /usr/local/lib/
   sudo ln -sf /usr/local/lib/libKvaserCAN.0.3.4.dylib /usr/local/lib/libKvaserCAN.dylib

   # 설치 확인
   ls -l /usr/local/lib/libUVCANKVL.dylib

   정상적으로 심볼릭 링크가 생성되었다면 아래와 유사한 출력이 나타납니다
   lrwxr-xr-x  1 root  staff  38  3 27 18:44 /usr/local/lib/libUVCANKVL.dylib -> /usr/local/lib/libUVCANKVL.0.3.4.dylib
   ```



   ```
## 사용 예시

### 기본적인 메시지 송신/수신

```python
from kvaser_can import KvaserCAN

# KvaserCAN 인스턴스 생성
can = KvaserCAN()

# 사용 가능한 채널 검색
channels = can.scan_channels()
if channels:
    # 첫 번째 채널 사용
    can.open(channel=channels[0])
    
    # CAN 컨트롤러 시작 (250kbit/s)
    can.start(bitrate_index=-3)
    
    # 메시지 송신
    can.send(msg_id=0x100, data=[0x11, 0x22, 0x33, 0x44])
    
    # 메시지 수신 (1초 타임아웃)
    result, msg = can.receive(timeout=1000)
    if result == 0:
        # 메시지 정보 출력
        print(f"ID: 0x{msg.id:X}, 데이터: {[msg.data[i] for i in range(msg.dlc)]}")
    
    # 채널 닫기
    can.close()
```

### CAN 버스 모니터링

```python
from kvaser_can import KvaserCAN
import time

# 메시지 콜백 함수
def message_handler(msg):
    # 메시지 데이터를 16진수로 변환
    data_bytes = [msg.data[i] for i in range(msg.dlc)]
    data_hex = [hex(b)[2:].zfill(2) for b in data_bytes]
    
    print(f"ID: 0x{msg.id:X}, 데이터: {' '.join(data_hex)}")
    return True  # 계속 모니터링

# KvaserCAN 인스턴스 생성
can = KvaserCAN()

try:
    # 첫 번째 채널 열기 (모니터 모드)
    can.open(channel=0, monitor_mode=True)
    
    # CAN 컨트롤러 시작
    can.start()
    
    # 30초 동안 버스 모니터링
    print("CAN 버스 모니터링 시작 (30초)...")
    msg_count = can.monitor(duration=30, callback=message_handler)
    print(f"모니터링 완료: {msg_count}개 메시지 수신됨")
    
finally:
    # 항상 채널 닫기
    can.close()
```

## 비트레이트 인덱스 참조

| 인덱스 | 비트레이트 |
|:------:|:----------:|
|   0    |  1000 kbit/s |
|   -1   |   800 kbit/s |
|   -2   |   500 kbit/s |
|   -3   |   250 kbit/s |
|   -4   |   125 kbit/s |
|   -5   |   100 kbit/s |
|   -6   |    50 kbit/s |
|   -7   |    20 kbit/s |
|   -8   |    10 kbit/s |

## 주의사항

실제 CAN 네트워크에 연결할 때는 주의하세요. 잘못된 메시지를 보내면 연결된 시스템에 손상을 줄 수 있습니다.

## 라이선스

이 프로젝트는 원본 [mac-can/KvaserCAN-Library](https://github.com/mac-can/KvaserCAN-Library)와 동일한 BSD 2-Clause License 하에 배포됩니다.

```
BSD 2-Clause License
Copyright (c) 2021, Uwe Vogt, UV Software
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

## 크레딧

이 프로젝트는 다음 소프트웨어를 기반으로 합니다:
- [mac-can/KvaserCAN-Library](https://github.com/mac-can/KvaserCAN-Library) by Uwe Vogt, UV Software
