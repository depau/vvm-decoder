#!/usr/bin/python3
# -*- coding: utf-8 -*-

import binascii
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar('T')

SMS_DATETIME_FORMAT = '%d/%m/%Y %H:%M %z'


class EventType(Enum):
    NEW_MESSAGE = b'NM'
    MAILBOX_UPDATE = b'MBU'
    GREETINGS = b'GU'

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        if self == self.NEW_MESSAGE:
            return 'New message'
        elif self == self.GREETINGS:
            return 'Greetings/VS update'
        elif self == self.MAILBOX_UPDATE:
            return 'Mailbox update'


class MessageType(Enum):
    VOICE = b'v'
    VIDEO = b'o'
    FAX = b'f'
    INFOTAINMENT = b'i'
    ECC = b'e'

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        if self == self.VOICE:
            return 'Voice message'
        elif self == self.VIDEO:
            return 'Video'
        elif self == self.FAX:
            return 'Fax'
        elif self == self.INFOTAINMENT:
            return 'Infotainment'
        elif self == self.ECC:
            return 'ECC.'


@dataclass
class VVMSyncSMS:
    event: EventType
    id: int
    count: int
    message_type: MessageType = None
    sender: str = None
    deposit_time: datetime = None
    length: int = None

    def repr_details(self) -> str:
        out = 'Event type:          {}\n'.format(self.event)
        out += 'ID:                  {}\n'.format(self.id)
        out += 'Messages in mailbox: {}\n'.format(self.count)
        if self.message_type:
            out += 'Message type:        {}\n'.format(self.message_type)
        if self.sender:
            out += 'From:                {}\n'.format(self.sender)
        if self.deposit_time:
            out += 'Time received:       {}\n'.format(self.deposit_time.strftime(SMS_DATETIME_FORMAT))
        if self.length:
            if self.message_type:
                if self.message_type in (MessageType.VOICE, MessageType.VIDEO, MessageType.INFOTAINMENT):
                    out += 'Duration:            {} seconds\n'.format(self.length)
                elif self.message_type == MessageType.FAX:
                    out += 'Pages:               {}\n'.format(self.length)
                else:
                    out += 'Length:              {}\n'.format(self.length)
            else:
                out += 'Length:              {}\n'.format(self.length)
        out = out[:-1]

        return out


@dataclass(frozen=True, eq=False)
class FieldDecoder:
    field_name: str
    decoder: Callable[[bytes], T]

    def decode(self, value: bytes) -> T:
        return self.decoder(value)


field_decoder_map = {
    b'ev': FieldDecoder('event', EventType),
    b'id': FieldDecoder('id', int),
    b'c': FieldDecoder('count', int),
    b't': FieldDecoder('message_type', MessageType),
    b's': FieldDecoder('sender', lambda value: value.decode()),
    b'dt': FieldDecoder('deposit_time', lambda value: datetime.strptime(value.decode(), SMS_DATETIME_FORMAT)),
    b'l': FieldDecoder('length', int)
}


def decode(binsms: bytes) -> VVMSyncSMS:
    splitsms = binsms.split(b':', 2)

    if splitsms[0] != b'//VVM':
        raise ValueError('Bytestring is not a valid visual voicemail SMS')
    binsms = binsms[4:]

    if splitsms[1] != b'SYNC':
        raise NotImplementedError('{} messages are not supported'.format(splitsms[1].decode()))

    params = [i.split(b'=', 1) for i in splitsms[2].split(b';')]

    binsms_kwargs = {}

    for name, value in params:
        if name not in field_decoder_map:
            warnings.warn('Field {} is not supported'.format(name.decode()))
            continue

        decoder = field_decoder_map[name]

        field_name = decoder.field_name
        field_value = decoder.decode(value)

        binsms_kwargs[field_name] = field_value

    return VVMSyncSMS(**binsms_kwargs)


def decode_from_bytestring(bytestr: str) -> VVMSyncSMS:
    binsms = binascii.unhexlify(bytestr)
    return decode(binsms)


if __name__ == "__main__":
    binsms_bytestr = sys.argv[1]
    print(decode_from_bytestring(binsms_bytestr).repr_details())
