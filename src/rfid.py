
class RFID:
    def __init__(self, sda=1, sck=2, mosi=3, miso=4, rst=0, spi_id=0):
        self.reader = MFRC522(spi_id=spi_id, sck=sck, mosi=mosi, miso=miso, cs=sda, rst=rst)
        self.reader.init()
        
    def uidToString(self, uid):
        string = ""
        for i in uid:
            string = "%02X" % i + string
        return string

    def readUid(self):
        self.reader.init()
        status, _ = self.reader.request(self.reader.REQIDL)
        if status != self.reader.OK: return False, False, False
        
        status, uid = self.reader.SelectTagSN()
        if status != self.reader.OK: return None, None, None
        
        return uid, int.from_bytes(bytes(uid),"little",False), self.uidToString(uid)
    
    def read(self):
        self.reader.init()
        status, _ = self.reader.request(self.reader.REQIDL)
        
        if status != self.reader.OK: return False
        status, uid = self.reader.SelectTagSN()
        
        if status != self.reader.OK: return None
        firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
        nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]
        
        content =  self.reader.getContent(uid)
        return content
    
    def readContent(self):
        bytes = self.read()
        if not bytes: return False
        content = ''
        
        group = 1
        while group < 16:
            for line in range(3):
                byteLine = bytes[group * 4 + line]
                for byte in byteLine:
                    
                    if byte:
                        content += chr(byte)
            group += 1
        
        return content
            
    def erase(self):
        access = RfidAccess()
        
        self.reader.init()
        status, tagType = self.reader.request(self.reader.REQIDL)

        if status == self.reader.OK:
            status, uid = self.reader.SelectTagSN()
            
            if status == self.reader.OK:
                firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
                nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]
                defaultKey = [255,255,255,255,255,255]

                access.decodeAccess(0xff, 0x07, 0x80)
                block3 = access.fillBlock3(keyA=defaultKey, keyB=defaultKey)
                
                self.reader.writeSectorBlock(uid, 0, 3, block3, keyB=defaultKey)
                
                datablock = 16 * [0]
                self.reader.writeSectorBlock(uid, 0, 1, datablock, keyB=defaultKey)
                self.reader.writeSectorBlock(uid, 0, 2, datablock, keyB=defaultKey)

                for s in range(1,16):
                    for b in range(3):
                        self.reader.writeSectorBlock(uid, s, b, datablock, keyB=defaultKey)
                    self.reader.writeSectorBlock(uid, s, 3, block3, keyB=defaultKey)
                return True
            return False
        
    def write(self, string):
        splitted = [ord(char) for char in string]
        access = RfidAccess()
                
        self.reader.init()
        status, _ = self.reader.request(self.reader.REQIDL)

        if status != self.reader.OK: return 'a'
        status, uid = self.reader.SelectTagSN()
    
        if status != self.reader.OK: return 'b'
        defaultKey = [255,255,255,255,255,255]

        firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
        nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]

        access.setTrailerAccess(keyA_Write=access.KEYB,access_Read=access.KEYAB,access_Write=access.KEYB,
                                keyB_Read=access.NEVER,keyB_Write=access.KEYB)
        
        access.setBlockAccess(access.ALLBLOCK, access_Read=access.KEYAB, access_Write=access.KEYB,
                              access_Inc=access.NEVER, access_Dec=access.NEVER)
        
        block3 = access.fillBlock3(keyA=firstSectorKey,keyB=defaultKey)
        
        if self.reader.writeSectorBlock(uid,0,3,block3,keyA=defaultKey) == self.reader.ERR:
            return 'c'
        
        b1 = [0x14,0x01,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1]
        self.reader.writeSectorBlock(uid,0,1,b1,keyB=defaultKey)

        b2 = [0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1,0x03,0xE1]
        self.reader.writeSectorBlock(uid,0,2,b1,keyB=defaultKey)
        
        access.setTrailerAccess(keyA_Write=access.KEYB,access_Read=access.KEYAB,access_Write=access.KEYB,
                                keyB_Read=access.NEVER,keyB_Write=access.KEYB)
        
        access.setBlockAccess(access.ALLBLOCK, access_Read=access.KEYAB, access_Write=access.KEYAB,
                              access_Inc=access.KEYAB, access_Dec=access.KEYAB)
        
        block3 = access.fillBlock3(keyA=nextSectorKey,keyB=defaultKey)
        
        for sector in range(1,16):
            for block in range(3):

                if len(splitted) > 16:
                    if self.reader.writeSectorBlock(
                        uid, sector, block,
                        splitted[0:16], keyA=defaultKey
                    ) == self.reader.ERR: return False
                    splitted = splitted[16::]
                
                elif len(splitted) > 0:
                    splitted.extend(
                            (16-len(splitted))*[0]
                    )
                    if self.reader.writeSectorBlock(
                        uid, sector, block,
                        splitted, keyA=defaultKey
                    ) == self.reader.ERR: return False
                    splitted = []
                else:
                    if self.reader.writeSectorBlock(
                        uid, sector, block,
                        [0]*16, keyA=defaultKey
                    ) == self.reader.ERR: return False
            
            if  self.reader.writeSectorBlock(uid, sector, 3, block3, keyA=defaultKey) == self.reader.ERR:
                return 'd'
            
        return True
    
    def printContent(self):
        self.reader.init()
        status, _ = self.reader.request(self.reader.REQIDL)
        if status != self.reader.OK: return False
        
        status, uid = self.reader.SelectTagSN()
        if status != self.reader.OK: return False
        
        firstSectorKey = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
        nextSectorKey = [0xD3, 0xF7, 0xD3, 0xF7, 0xD3, 0xF7]
        
        if self.reader.MFRC522_DumpClassic1K(uid, Start=0, End=4, keyA=firstSectorKey) == self.reader.OK:
            self.reader.MFRC522_DumpClassic1K(uid, Start=4, End=64, keyA=nextSectorKey)
            return True
        
        return False
    
    def rewrite(self, content):
        if not self.erase(): return False
        if not self.write(content): return False
        return True
