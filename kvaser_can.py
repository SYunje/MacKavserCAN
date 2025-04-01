#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kvaser CAN 클래스 라이브러리
"""
import sys
import platform
import time
from typing import List, Tuple, Optional, Union
import os

"""
KvaserCAN Python 클래스 라이브러리

이 모듈은 Kvaser CAN 인터페이스를 Python에서 쉽게 사용할 수 있도록 
객체지향적인 클래스 기반 API를 제공합니다.

BSD 2-Clause License
Copyright (c) 2021, Uwe Vogt, UV Software
All rights reserved.

원본 저작물: https://github.com/mac-can/KvaserCAN-Library

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
"""

# 사용자 홈 디렉토리 가져오기
home_dir = os.path.expanduser('~')
# KvaserCAN-Library 예제 경로 설정
canapi_path = os.path.join(home_dir, 'KvaserCAN-Library', 'Examples', 'Python')

# CANAPI 모듈 경로 추가
sys.path.append(canapi_path)
from CANAPI import CANAPI, OpMode, Bitrate, Message, Status
from CANAPI import CANMODE_DEFAULT, CANBTR_INDEX_250K, CANREAD_INFINITE
from CANAPI import CANERR_NOERROR, CANERR_RX_EMPTY


class KvaserCAN:
    """
    Kvaser CAN 인터페이스 클래스
    """

    def __init__(self, lib_name: str = None):
        """
        Kvaser CAN 클래스 초기화

        Args:
            lib_name: 드라이버 라이브러리 파일명 (None이면 자동 선택)
        """
        # 드라이버 라이브러리 파일명 자동 선택
        if lib_name is None:
            if platform.system() == 'Darwin':
                lib_name = 'libUVCANKVL.dylib'
            elif platform.system() != 'Windows':
                lib_name = 'libuvcankvl.so.1'
            else:
                lib_name = 'u3cankvl.dll'

        # API 인스턴스 생성
        self.api = CANAPI(lib_name)
        self.channel = -1
        self.is_initialized = False
        self.is_started = False

        # 드라이버 버전 정보
        self.version = self.api.version()

    def __del__(self):
        """소멸자: 채널이 열려있으면 닫기"""
        self.close()

    def open(self, channel: int = 0, monitor_mode: bool = False) -> int:
        """
        CAN 채널 열기

        Args:
            channel: CAN 채널 번호
            monitor_mode: 모니터 모드 활성화 여부

        Returns:
            0 성공, 음수 오류 코드
        """
        # 이미 초기화되어 있으면 닫기
        if self.is_initialized:
            self.close()

        # 작동 모드 설정
        op_mode = OpMode()
        op_mode.byte = CANMODE_DEFAULT

        # 모니터 모드 활성화 (요청 시)
        if monitor_mode:
            op_mode.bits.mon = 1

        # 채널 초기화
        result = self.api.init(channel=channel, mode=op_mode)

        if result == CANERR_NOERROR:
            self.channel = channel
            self.is_initialized = True

        return result

    def start(self, bitrate_index: int = -3) -> int:
        """
        CAN 컨트롤러 시작

        Args:
            bitrate_index: 비트레이트 인덱스 (-3=250kbps, 0=1Mbps 등)

        Returns:
            0 성공, 음수 오류 코드
        """
        if not self.is_initialized:
            return -95  # CANERR_NOTINIT

        # 비트레이트 설정
        bit_rate = Bitrate()
        bit_rate.index = bitrate_index

        # CAN 컨트롤러 시작
        result = self.api.start(bitrate=bit_rate)

        if result == CANERR_NOERROR:
            self.is_started = True

        return result

    def close(self) -> int:
        """
        CAN 채널 닫기

        Returns:
            0 성공, 음수 오류 코드
        """
        result = CANERR_NOERROR

        if self.is_started:
            # CAN 컨트롤러 중지
            result = self.api.reset()
            self.is_started = False

        if self.is_initialized:
            # CAN 인터페이스 종료
            result = self.api.exit()
            self.is_initialized = False
            self.channel = -1

        return result

    def send(self, msg_id: int, data: Union[bytes, List[int]], extended_id: bool = False,
             remote_frame: bool = False, timeout: int = 0) -> int:
        """
        CAN 메시지 송신

        Args:
            msg_id: CAN 메시지 ID
            data: 송신할 데이터 (bytes 또는 정수 리스트)
            extended_id: 확장 ID 사용 여부 (29비트)
            remote_frame: 원격 프레임 여부
            timeout: 송신 타임아웃 (밀리초)

        Returns:
            0 성공, 음수 오류 코드
        """
        if not self.is_started:
            return -95  # CANERR_NOTINIT

        # 메시지 생성
        msg = Message()
        msg.id = msg_id

        # 데이터가 bytes 타입이 아니면 변환
        if not isinstance(data, bytes):
            data = bytes(data)

        # 데이터 길이
        data_len = len(data)
        if data_len > 8:  # CAN 2.0은 최대 8바이트
            data_len = 8
            data = data[:8]

        # 메시지에 데이터 설정
        for i in range(data_len):
            msg.data[i] = data[i]

        msg.dlc = data_len

        # 메시지 플래그 설정
        msg.flags.xtd = 1 if extended_id else 0
        msg.flags.rtr = 1 if remote_frame else 0
        msg.flags.fdf = 0  # CAN 2.0 프레임
        msg.flags.brs = 0  # 비트레이트 스위칭 없음
        msg.flags.esi = 0  # 에러 상태 인디케이터

        # 메시지 송신
        return self.api.write(message=msg, timeout=timeout)

    def receive(self, timeout: int = 1000) -> Tuple[int, Optional[Message]]:
        """
        CAN 메시지 수신

        Args:
            timeout: 수신 타임아웃 (밀리초)

        Returns:
            (결과, 메시지) 튜플. 결과가 0이 아니면 메시지는 None
        """
        if not self.is_started:
            return -95, None  # CANERR_NOTINIT

        # 메시지 수신
        return self.api.read(timeout=timeout)

    def get_status(self) -> Tuple[int, Optional[Status]]:
        """
        CAN 상태 확인

        Returns:
            (결과, 상태) 튜플. 결과가 0이 아니면 상태는 None
        """
        if not self.is_initialized:
            return -95, None  # CANERR_NOTINIT

        return self.api.status()

    def get_busload(self) -> Tuple[int, float, Status]:
        """
        CAN 버스 부하 확인

        Returns:
            (결과, 버스부하, 상태) 튜플
        """
        if not self.is_initialized:
            return -95, 0.0, None  # CANERR_NOTINIT

        return self.api.busload()

    def get_bitrate(self) -> Tuple[int, Bitrate, object]:
        """
        CAN 비트레이트 정보 확인

        Returns:
            (결과, 비트레이트, 속도) 튜플
        """
        if not self.is_initialized:
            return -95, None, None  # CANERR_NOTINIT

        return self.api.bitrate()

    def scan_channels(self, max_channels: int = 8) -> List[int]:
        """
        사용 가능한 CAN 채널 검색

        Args:
            max_channels: 검색할 최대 채널 수

        Returns:
            사용 가능한 채널 번호 목록
        """
        available_channels = []

        for channel in range(max_channels):
            op_mode = OpMode()
            op_mode.byte = CANMODE_DEFAULT

            # 채널 테스트
            result, state = self.api.test(channel=channel, mode=op_mode)

            if state == 0:  # 채널이 존재하고 사용 가능
                available_channels.append(channel)

        return available_channels

    def monitor(self, duration: int = 30, callback=None) -> int:
        """
        CAN 버스 모니터링

        Args:
            duration: 모니터링 지속 시간 (초)
            callback: 메시지 수신 시 호출할 콜백 함수
                      함수 시그니처: callback(msg: Message) -> bool
                      반환값이 False이면 모니터링 중단

        Returns:
            수신한 메시지 개수
        """
        if not self.is_started:
            return -95  # CANERR_NOTINIT

        msg_count = 0
        start_time = time.time()

        try:
            while (time.time() - start_time) < duration:
                # 비차단 읽기 (타임아웃 100ms)
                result, msg = self.api.read(timeout=100)

                if result == CANERR_NOERROR:
                    msg_count += 1

                    # 콜백 함수 호출 (있는 경우)
                    if callback is not None:
                        # 콜백이 False를 반환하면 중단
                        if not callback(msg):
                            break
                elif result != CANERR_RX_EMPTY:
                    # 타임아웃(-30)이 아닌 다른 오류면 중단
                    break

        except KeyboardInterrupt:
            pass

        return msg_count
