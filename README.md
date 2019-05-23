# Visual voicemail SMS decoder

Currently only supports `SYNC` messages.

Specification: https://www.gsma.com/newsroom/wp-content/uploads/2012/07/OMTP_VVM_Specification_1_3.pdf

## Usage

```txt
./vvm_decoder.py <binary sms as HEX string>
```

```txt
$ ./vvm_decoder.py 2f2f56564d3a53594e433a65763d4e4d3b69643d31373b633d313b743d763b733d2b313233343536373839303b64743d32332f30352f323031392031323a3239202b303230303b6c3d35
Event type:          New message
ID:                  17
Messages in mailbox: 1
Message type:        Voice message
From:                +1234567890
Time received:       23/05/2019 12:29 +0200
Duration:            5 seconds
```


