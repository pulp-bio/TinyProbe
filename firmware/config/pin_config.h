/**
 * @file pin_config.h
 *
 * @brief TinyProbe/WiUS board pin assignments
 *
 * @date 22.09.2026
 * @copyright Copyright (C) 2026 ETH Zurich. All rights reserved.
 *
 * @ingroup wius
 *
 * @details
 *
 * Project-owned TinyProbe/WiUS board pin assignments. Maintain this file in
 * source control; it is not generated SDK configuration.
 *
 * The SDK's RTE_Device_917.h consumes these macro names. HP is the SDK's
 * high-performance GPIO port; LOC values select the corresponding pin routes.
 *
 * @parblock
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * @endparblock
 *
 */

#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

/* SSI: MOSI GPIO 26, MISO GPIO 27, clock GPIO 25, chip select GPIO 28. */
#ifndef SSI_MASTER_MOSI_DATA0_PORT
#define SSI_MASTER_MOSI_DATA0_PORT HP
#endif
#ifndef SSI_MASTER_MOSI_DATA0_PIN
#define SSI_MASTER_MOSI_DATA0_PIN 26
#endif
#ifndef SSI_MASTER_DATA0_LOC
#define SSI_MASTER_DATA0_LOC 1
#endif

#ifndef SSI_MASTER_MISO_DATA1_PORT
#define SSI_MASTER_MISO_DATA1_PORT HP
#endif
#ifndef SSI_MASTER_MISO_DATA1_PIN
#define SSI_MASTER_MISO_DATA1_PIN 27
#endif
#ifndef SSI_MASTER_DATA1_LOC
#define SSI_MASTER_DATA1_LOC 4
#endif

#ifndef SSI_MASTER_SCK__PORT
#define SSI_MASTER_SCK__PORT HP
#endif
#ifndef SSI_MASTER_SCK__PIN
#define SSI_MASTER_SCK__PIN 25
#endif
#ifndef SSI_MASTER_SCK_LOC
#define SSI_MASTER_SCK_LOC 7
#endif

#ifndef SSI_MASTER_CS0__PORT
#define SSI_MASTER_CS0__PORT HP
#endif
#ifndef SSI_MASTER_CS0__PIN
#define SSI_MASTER_CS0__PIN 28
#endif
#ifndef SSI_MASTER_CS0_LOC
#define SSI_MASTER_CS0_LOC 10
#endif


/* GSPI: MOSI GPIO 27, MISO GPIO 26, clock GPIO 25, chip select GPIO 28. */
#ifndef GSPI_MASTER_MOSI__PORT
#define GSPI_MASTER_MOSI__PORT HP
#endif
#ifndef GSPI_MASTER_MOSI__PIN
#define GSPI_MASTER_MOSI__PIN 27
#endif
#ifndef GSPI_MASTER_MOSI_LOC
#define GSPI_MASTER_MOSI_LOC 17
#endif

#ifndef GSPI_MASTER_MISO__PORT
#define GSPI_MASTER_MISO__PORT HP
#endif
#ifndef GSPI_MASTER_MISO__PIN
#define GSPI_MASTER_MISO__PIN 26
#endif
#ifndef GSPI_MASTER_MISO_LOC
#define GSPI_MASTER_MISO_LOC 22
#endif

#ifndef GSPI_MASTER_SCK__PORT
#define GSPI_MASTER_SCK__PORT HP
#endif
#ifndef GSPI_MASTER_SCK__PIN
#define GSPI_MASTER_SCK__PIN 25
#endif
#ifndef GSPI_MASTER_SCK_LOC
#define GSPI_MASTER_SCK_LOC 1
#endif

#ifndef GSPI_MASTER_CS0__PORT
#define GSPI_MASTER_CS0__PORT HP
#endif
#ifndef GSPI_MASTER_CS0__PIN
#define GSPI_MASTER_CS0__PIN 28
#endif
#ifndef GSPI_MASTER_CS0_LOC
#define GSPI_MASTER_CS0_LOC 5
#endif

#endif /* PIN_CONFIG_H */
