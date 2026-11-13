#ifndef __SSD1306_H
#define __SSD1306_H
#include "main.h"

#define OLED_ADDR 0x7A  

void SSD1306_Init(void);
void SSD1306_Clear(void);
void SSD1306_SetPos(uint8_t x, uint8_t page);
void SSD1306_PrintString(char *str);

#endif
