from enum import Enum
from dataclasses import dataclass

ATCCmdType = Enum('ATCCmdType', ('Speed', 'Altitude', 'LateralOffset'))


class ATCCmd:
    pass


@dataclass
class AltCmd(ATCCmd):
    delta: float
    targetAlt: float
    assignTime: int = 0
    cmdType = ATCCmdType.Altitude

    def __str__(self):
        return 'ALTCMD: <TIME:%d, DELTA:%0.2f,TARGET:%0.2f>'%(self.assignTime, self.delta, self.targetAlt)

    def __repr__(self):
        return 'ALTCMD: <TIME:%d, DELTA:%0.2f,TARGET:%0.2f>'%(self.assignTime, self.delta, self.targetAlt)


@dataclass
class SpdCmd(ATCCmd):
    delta: float
    targetTAS: float
    assignTime: int = 0
    cmdType = ATCCmdType.Speed

    def __str__(self):
        return 'SPDCMD: <TIME:%d, DELTA:%0.2f,TARGET:%0.2f>'%(self.assignTime, self.delta, self.targetTAS)

    def __repr__(self):
        return 'SPDCMD: <TIME:%d, DELTA:%0.2f,TARGET:%0.2f>'%(self.assignTime, self.delta, self.targetTAS)


@dataclass
class LateralOffset(ATCCmd):
    distance: float
    assignTime: int = 0
    cmdType = ATCCmdType.LateralOffset

    def __str__(self):
        return 'OFFSET: <TIME: %d, DIST: %d>' % (self.assignTime, self.distance)

    def __repr__(self):
        return 'OFFSET: <TIME: %d, DIST: %d>' % (self.assignTime, self.distance)
