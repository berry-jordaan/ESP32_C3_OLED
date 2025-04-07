# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
"""
Based on :https://github.com/stlehmann/micropython-ssd1306/blob/master/ssd1306.py 
2015-2016 Stefan Lehmann

This class is specific to the following OLED display controller (ESP32-C3 OLED):
https://www.aliexpress.com/item/1005007342383107.html

This driver is only as useful as the display it is connected to.
It is not a general purpose driver for all SSD1306 displays.

Limitations:
- The display must be 128x64 pixels. (only)
- The display must be connected to the ESP32-C3 using I2C or SPI.
- The display must be compatible with the SSD1306 controller.
- The display must be compatible with MicroPython.(ESP32_GENERIC_C3-20241129-v1.24.1.bin)
- The display must be compatible with the ESP32-C3 MicroPython firmware. 
"""

from micropython import const
import framebuf

# register definitions
SET_CONTRAST = const(0x81)
SET_ENTIRE_ON = const(0xA4)
SET_NORM_INV = const(0xA6)
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP = const(0xA0)
SET_MUX_RATIO = const(0xA8)
SET_COM_OUT_DIR = const(0xC0)
SET_DISP_OFFSET = const(0xD3)
SET_COM_PIN_CFG = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE = const(0xD9)
SET_VCOM_DESEL = const(0xDB)
SET_CHARGE_PUMP = const(0x8D)

SET_FB_WIDTH = const(128)
SET_FB_HEIGHT = const(64)
SET_X_OFFSET = const(28)
SET_Y_OFFSET = const(24)

# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class SSD1306(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            SET_DISP | 0x00,  # off
            # address setting
            SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            SET_MUX_RATIO,
            self.height - 1,
            SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            SET_DISP_OFFSET,
            0x00,
            SET_COM_PIN_CFG,
            0x02 if self.width > 2 * self.height else 0x12,
            # timing and driving scheme
            SET_DISP_CLK_DIV,
            0x80,
            SET_PRECHARGE,
            0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            SET_CONTRAST,
            0xFF,  # maximum
            SET_ENTIRE_ON,  # output follows RAM contents
            SET_NORM_INV,  # not inverted
            # charge pump
            SET_CHARGE_PUMP,
            0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01,
        ):  # on
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def poweroff(self):
        self.write_cmd(SET_DISP | 0x00)

    def poweron(self):
        self.write_cmd(SET_DISP | 0x01)

    def contrast(self, contrast):
        self.write_cmd(SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(SET_NORM_INV | (invert & 1))

    def show(self):
        x0 = 0
        x1 = self.width - 1
        self.write_cmd(SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)

    def write_cmd(self, cmd):
        pass

    def write_data(self, buf):
        pass

'''
# ESP32-C3 OLED driver
# This will take care of the offset of the framebuffer
'''
class ESP32_C3_OLED(SSD1306):
    def __init__(self, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b"\x40", None]  # Co=0, D/C#=1
        super().__init__(SET_FB_WIDTH, SET_FB_HEIGHT, external_vcc)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.write_list[1] = buf
        self.i2c.writevto(self.addr, self.write_list)

    def rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        super().rect(x + SET_X_OFFSET, y + SET_Y_OFFSET, w, h, c)

    def text(self, s: str, x: int, y: int, c: int = 1) -> None:
        super().text(s, x + SET_X_OFFSET, y + SET_Y_OFFSET, c)

    def ellipse(self, x, y, xr, yr, c, f = 'True')-> None:
        super().ellipse(x + SET_X_OFFSET, y + SET_Y_OFFSET, xr, yr, c, f)

    def line(self, x1: int, y1: int, x2: int, y2: int, c: int) -> None:
        super().line(x1 + SET_X_OFFSET, y1 + SET_Y_OFFSET, x2 + SET_X_OFFSET, y2 + SET_Y_OFFSET, c)

    def vline(self, x: int, y: int, h: int, c: int) -> None:
        super().vline(x + SET_X_OFFSET, y + SET_Y_OFFSET, h, c)

    def hline(self, x: int, y: int, w: int, c: int) -> None:
        super().hline(x + SET_X_OFFSET, y + SET_Y_OFFSET, w, c)

    def pixel(self, x: int, y: int, c: int) -> None:
        super().pixel(x + SET_X_OFFSET, y + SET_Y_OFFSET, c)

    def fill_rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        super().fill_rect(x + SET_X_OFFSET, y + SET_Y_OFFSET, w, h, c)
        