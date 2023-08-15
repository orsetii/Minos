
from machine import Pin, SPI
import framebuf
import minos_network
import utime
import ujson

WF_PARTIAL_2IN13_V3= [
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x14,0x0,0x0,0x0,0x0,0x0,0x0,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
    0x22,0x17,0x41,0x00,0x32,0x36,
]

WS_20_30_2IN13_V3 = [ 
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0xF,0x0,0x0,0xF,0x0,0x0,0x2,    
    0xF,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,    
    0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,  
    0x22,0x17,0x41,0x0,0x32,0x36  
]

EPD_WIDTH       = 122
EPD_HEIGHT      = 250

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

class EPD_2in13_V3_Portrait(framebuf.FrameBuffer):
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else :
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT
        
        self.full_lut = WF_PARTIAL_2IN13_V3
        self.partial_lut = WS_20_30_2IN13_V3
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.buffer = bytearray(self.height * self.width // 8)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        self.init()
    
    '''
    function :Change the pin state
    parameter:
        pin : pin
        value : state
    '''
    def digital_write(self, pin, value):
        pin.value(value)

    '''
    function : Read the pin state 
    parameter:
        pin : pin
    '''
    def digital_read(self, pin):
        return pin.value()

    '''
    function : The time delay function
    parameter:
        delaytime : ms
    '''
    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)
        
    '''
    function : Write data to SPI
    parameter:
        data : data
    '''
    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    '''
    function :Hardware reset
    parameter:
    '''
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(20)   

    '''
    function :send command
    parameter:
     command : Command register
    '''
    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :send data
    parameter:
     data : Write data
    '''
    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data1(self, buf):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi.write(bytearray(buf))
        self.digital_write(self.cs_pin, 1)
    
    '''
    function :Wait until the busy_pin goes LOW
    parameter:
    '''
    def ReadBusy(self):
        print('busy')
        self.delay_ms(10)
        while(self.digital_read(self.busy_pin) == 1):      # 0: idle, 1: busy
            self.delay_ms(10)    
        print('busy release')
    
    '''
    function : Turn On Display
    parameter:
    '''
    def TurnOnDisplay(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20)  #  Activate Display Update Sequence    
        self.ReadBusy()
    
    '''
    function : Turn On Display Part
    parameter:
    '''
    def TurnOnDisplayPart(self):
        self.send_command(0x22)  # Display Update Control
        self.send_data(0x0F)     # fast:0x0c, quality:0x0f, 0xcf
        self.send_command(0x20)  # Activate Display Update Sequence 
        self.ReadBusy()
    
    '''
    function : Set lut
    parameter:
        lut : lut data
    '''
    def LUT(self, lut):
        self.send_command(0x32)
        self.send_data1(lut[0:153])
        self.ReadBusy()
    
    '''
    function : Send lut data and configuration
    parameter:
        lut : lut data 
    '''
    def LUT_by_host(self, lut):
        self.LUT(lut)             # lut
        self.send_command(0x3F)
        self.send_data(lut[153])
        self.send_command(0x03)   # gate voltage
        self.send_data(lut[154])
        self.send_command(0x04)   # source voltage
        self.send_data(lut[155])  # VSH
        self.send_data(lut[156])  # VSH2
        self.send_data(lut[157])  # VSL
        self.send_command(0x2C)   # VCOM
        self.send_data(lut[158])
    
    '''
    function : Setting the display window
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
        Xend : End position of X-axis
        Yend : End position of Y-axis
    '''
    def SetWindows(self, Xstart, Ystart, Xend, Yend):
        self.send_command(0x44)                #  SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data((Xstart >> 3) & 0xFF)
        self.send_data((Xend >> 3) & 0xFF)
        
        self.send_command(0x45)                #  SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)
        self.send_data(Yend & 0xFF)
        self.send_data((Yend >> 8) & 0xFF)
        
    '''
    function : Set Cursor
    parameter:
        Xstart : X-axis starting position
        Ystart : Y-axis starting position
    '''
    def SetCursor(self, Xstart, Ystart):
        self.send_command(0x4E)             #  SET_RAM_X_ADDRESS_COUNTER
        self.send_data(Xstart & 0xFF)
        
        self.send_command(0x4F)             #  SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(Ystart & 0xFF)
        self.send_data((Ystart >> 8) & 0xFF)

    '''
    function : Initialize the e-Paper register
    parameter:
    '''
    def init(self):
        print('init')
        self.reset()
        self.delay_ms(100)
        
        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()
        
        self.send_command(0x01)  # Driver output control 
        self.send_data(0xf9)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x11)  #data entry mode 
        self.send_data(0x03)
        
        self.SetWindows(0, 0, self.width-1, self.height-1)
        self.SetCursor(0, 0)
        
        self.send_command(0x3C)  # BorderWaveform
        self.send_data(0x05)
        
        self.send_command(0x21) # Display update control
        self.send_data(0x00)
        self.send_data(0x80)
        
        self.send_command(0x18) # Read built-in temperature sensor
        self.send_data(0x80)
        
        self.ReadBusy()
        self.LUT_by_host(self.partial_lut)
       
    '''
    function : Clear screen
    parameter:
    '''
    def Clear(self):
        self.send_command(0x24)
        self.send_data1([0xff] * self.height * int(self.width / 8))
                
        self.TurnOnDisplay()    
    
    '''
    function : Sends the image buffer in RAM to e-Paper and displays
    parameter:
        image : Image data
    '''
    def display(self, image):
        self.send_command(0x24)
        self.send_data1(image)
                
        self.TurnOnDisplay()
    
    '''
    function : Refresh a base image
    parameter:
        image : Image data
    '''
    def Display_Base(self, image):
        self.send_command(0x24)
        self.send_data1(image)
                
        self.send_command(0x26)
        self.send_data1(image)
                
        self.TurnOnDisplay()
        
    '''
    function : Sends the image buffer in RAM to e-Paper and partial refresh
    parameter:
        image : Image data
    '''    
    def display_Partial(self, image):
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(1)
        self.digital_write(self.reset_pin, 1)
        
        self.LUT_by_host(self.full_lut)
        
        self.send_command(0x37)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x40)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x3C)
        self.send_data(0x80)
        
        self.send_command(0x22)
        self.send_data(0xC0)
        self.send_command(0x20)
        self.ReadBusy()
        
        self.SetWindows(0,0,self.width-1,self.height-1)
        self.SetCursor(0,0)
        
        self.send_command(0x24)
        self.send_data1(image)

        self.TurnOnDisplayPart()
    
    '''
    function : Enter sleep mode
    parameter:
    '''
    def sleep(self):
        self.send_command(0x10) #enter deep sleep
        self.send_data(0x01)
        self.delay_ms(100)
 
 
isError = False 
 
def clear_connected_devices_screen_portion(epd):
    epd.fill_rect(5, 205, 110, 8, 0xFF)
    
def clear_entire_connected_devices_screen_portion(epd):
    epd.fill_rect(5, 205, 110, 30, 0xFF)
    

def update_display(epd, healthy, connectedDevices, currentInternal, currentExternal):
    update_hive_status_display(epd, healthy, connectedDevices)
    update_temperature_display(epd, currentInternal, currentExternal)
    update_clock(epd)

def clear_clock_time(epd):
    epd.fill_rect(2, 48, 113, 9, 0xFF)
    
def clear_clock_date(epd):
    epd.fill_rect(2, 32, 113, 9, 0xFF)

def update_clock(epd):
    try:
        date = minos_network.get_date()
        epd.text("  " + date.decode("utf-8"), 2, 32, 0x00)
        now = minos_network.get_time_no_seconds().decode("utf-8")
        if "00" in now:
            clear_clock_date(epd);
        clear_clock_time(epd);
        epd.text("     " + now, 2, 48, 0x00)
    except:
        clear_clock_time(epd)
        isError = True
        epd.text(" Network Issue", 2, 48, 0x00)
        
        
    
    
def update_hive_status_display(epd, healthy, connectedDevices):
    try:
        hive_status = minos_network.hive_status()
        hiveJson = ujson.loads(hive_status)

        
        jsonHealthy = hiveJson["healthy"]

        if jsonHealthy != healthy:
            healthy = jsonHealthy
            if healthy is True:
                epd.text("No Issues", 5, 218, 0x00)
            else:
                epd.text("⚠ Issue(s) Reported ⚠", 5, 218, 0x00)
        else:
            epd.text("No Issues", 5, 218, 0x00)
         
        if connectedDevices != str(len(hiveJson["devices"])):
            connectedDevices = str(len(hiveJson["devices"]))
            clear_connected_devices_screen_portion(epd);
            epd.text("Connected: " + connectedDevices, 5, 205, 0x00)
    except:
        clear_entire_connected_devices_screen_portion(epd)        
        epd.text("Network Issue", 5, 218, 0x00)
        
    
def clear_temp_display_screen_portion_int(epd):
    epd.fill_rect(8, 165, 60, 9, 0xFF)
    
def clear_temp_display_screen_portion_ext(epd):
    epd.fill_rect(73, 165, 42, 9, 0xFF)
    
def clear_temp_display_text(epd):
    epd.fill_rect(12, 153, 103, 8, 0xFF)
    
    
def update_temperature_display(epd, internal, external):
    try:
        temperature_text(epd)
        temp_res = minos_network.get_internal_temp();
        tempJson = ujson.loads(temp_res)    
        temp_value = float(tempJson["temp"])
        if internal != temp_value:
            clear_temp_display_screen_portion_int(epd)
            epd.text("{:05.2f}".format(temp_value), 8, 165, 0x00)
            
            
        temp_res = minos_network.get_external_temp();
        tempJson = ujson.loads(temp_res)
        
        temp_value = float(tempJson["temp"])
        if external != temp_value:
            clear_temp_display_screen_portion_ext(epd)
            epd.text("{:05.2f}".format(temp_value), 73, 165, 0x00)
            
    except:
        clear_temp_display_screen_portion_int(epd)
        clear_temp_display_screen_portion_ext(epd)
        clear_temp_display_text(epd)
        isError = True
        epd.text("Network Issue", 8, 165, 0x00)
        
        
         
        
    
def temperature_text(epd):
    epd.text("Temperatures(C)", 2, 140, 0x00)
    epd.text("Int", 12, 153, 0x00)
    epd.text("Ext", 81, 153, 0x00)


def main(name):
    healthy = True
    connectedDevices = "N/A"
    currentInternal = 0.00
    currentExternal = 0.00
    
    epd = EPD_2in13_V3_Portrait()
    epd.Clear()
    
    epd.fill(0xff)
    epd.text(name, 2, 0, 0x00)

    epd.text("Hive Status", 2, 192, 0x00)
    epd.rect(0, 200, 117, 40, 0x00)
    epd.text("No Issues", 5, 218, 0x00)
    
    
    temperature_text(epd)
    epd.rect(0, 148, 117, 40, 0x00)
    
    epd.text("Clock", 2, 16, 0x00)
    epd.rect(0, 24, 117, 40, 0x00)
    
    
    update_display(epd, healthy, connectedDevices, currentInternal, currentExternal)
    epd.display(epd.buffer)
    
    
    while True:
        epd.delay_ms(10000)
        update_display(epd, healthy, connectedDevices, currentInternal, currentExternal)                    
        epd.display_Partial(epd.buffer)


