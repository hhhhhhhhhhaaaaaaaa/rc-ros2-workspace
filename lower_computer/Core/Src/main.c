/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : ROS2 cmd_vel serial receiver + echo test
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "i2c.h"
#include "usart.h"
#include "gpio.h"
#include "oled.h"
#include <string.h>
#include <stdio.h>

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
uint8_t usart1_rx;
uint8_t rx_buf[8];
uint8_t rx_idx = 0;
uint8_t rx_state = 0;
float g_vx = 0.0f, g_vy = 0.0f;
char echo_buf[64];
char oled_buf[32];
char oled_text[128];
uint8_t text_idx = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_I2C1_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
  // ??????
  char *hello = "STM32 Ready\r\n";
  HAL_UART_Transmit(&huart1, (uint8_t*)hello, strlen(hello), 100);

  // OLED 初始化并显示欢迎�?
  OLED_Init();
  OLED_NewFrame();
  OLED_PrintASCIIString(0, 0, "ROS2 OLED Ready", &afont8x6, OLED_COLOR_NORMAL);
  OLED_ShowFrame();

  HAL_UART_Receive_IT(&huart1, &usart1_rx, 1);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if(huart->Instance == USART1)
    {
        uint8_t ch = usart1_rx;

        switch(rx_state) {
            case 0:
                if(ch == 0xAB) rx_state = 10;
                else if(ch == 0xAA) rx_state = 1;
                break;
            case 10:
                if(ch == 0xCD) { rx_state = 11; text_idx = 0; }
                else rx_state = 0;
                break;
            case 11:
                if(ch == 0x0D) {
                    oled_text[text_idx] = 0;
                    OLED_NewFrame();
                    OLED_PrintASCIIString(0, 0, oled_text, &afont8x6, OLED_COLOR_NORMAL);
                    OLED_ShowFrame();
                    rx_state = 0;
                } else {
                    if(text_idx < 127) oled_text[text_idx++] = ch;
                }
                break;
            case 1:
                if(ch == 0x55) { rx_state = 2; rx_idx = 0; }
                else rx_state = 0;
                break;
            case 2:
                rx_buf[rx_idx++] = ch;
                if(rx_idx >= 8) rx_state = 3;
                break;
            case 3:
                {
                    uint8_t sum = 0xAA + 0x55;
                    for(int i=0; i<8; i++) sum += rx_buf[i];
                    if((sum & 0xFF) == ch) {
                        memcpy(&g_vx, rx_buf, 4);
                        memcpy(&g_vy, rx_buf+4, 4);

                        // ?????(Windows???????)
                        sprintf(echo_buf, "OK vx:%.3f vy:%.3f\r\n", g_vx, g_vy);
                        HAL_UART_Transmit(&huart1, (uint8_t*)echo_buf, strlen(echo_buf), 100);

                        // �? OLED 上显�? vx/vy
                        OLED_NewFrame();
                        sprintf(oled_buf, "vx:%.2f", g_vx);
                        OLED_PrintASCIIString(0, 0, oled_buf, &afont8x6, OLED_COLOR_NORMAL);
                        sprintf(oled_buf, "vy:%.2f", g_vy);
                        OLED_PrintASCIIString(0, 16, oled_buf, &afont8x6, OLED_COLOR_NORMAL);
                        OLED_ShowFrame();
                    } else {
                        // ???????
                        char *err = "ERR checksum\r\n";
                        HAL_UART_Transmit(&huart1, (uint8_t*)err, strlen(err), 100);
                    }
                }
                rx_state = 0;
                break;
        }

        HAL_UART_Receive_IT(&huart1, &usart1_rx, 1);
    }
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
