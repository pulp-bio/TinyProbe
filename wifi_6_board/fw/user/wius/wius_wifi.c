/**
 * @file wius_wifi.c
 *
 * @brief WiFi implementation for WiUS source file
 *
 * @author Cédric Hirschi, ETH Zürich
 * @date 28.04.2025
 *
 * @ingroup wius
 *
 */

#include "wius_wifi.h"

#include "sl_utility.h"
#include "sl_wifi.h"
#include "sl_net.h"
#include "sl_net_default_values.h"
#include "sl_net_wifi_types.h"

#ifndef WIUS_WIFI_FILTER_BROADCAST
#define WIUS_WIFI_FILTER_BROADCAST 0 /**< Whether to filter the WiFi broadcast */
#endif

#if WIUS_WIFI_FILTER_BROADCAST
#define BROADCAST_DROP_THRESHOLD 5000
#define BROADCAST_IN_TIM 1
#define BROADCAST_TIM_TILL_NEXT_COMMAND 1
#endif

static const sl_wifi_device_configuration_t station_init_configuration = {
    .boot_option = LOAD_NWP_FW,
    .mac_address = NULL,
    .band = SL_SI91X_WIFI_BAND_2_4GHZ,
    .region_code = EU,
    .boot_config = {
        .oper_mode = SL_SI91X_CLIENT_MODE,
        .coex_mode = SL_SI91X_WLAN_ONLY_MODE,
        .feature_bit_map = (SL_SI91X_FEAT_SECURITY_OPEN | SL_SI91X_FEAT_AGGREGATION | SL_SI91X_FEAT_WPS_DISABLE),
        .tcp_ip_feature_bit_map = (SL_SI91X_TCP_IP_FEAT_DHCPV4_CLIENT | SL_SI91X_TCP_IP_FEAT_SSL | SL_SI91X_TCP_IP_FEAT_EXTENSION_VALID),
        .custom_feature_bit_map = (SL_SI91X_CUSTOM_FEAT_EXTENTION_VALID | SL_SI91X_CUSTOM_FEAT_SOC_CLK_CONFIG_160MHZ),
        .ext_custom_feature_bit_map = (MEMORY_CONFIG | SL_SI91X_EXT_FEAT_FRONT_END_SWITCH_PINS_ULP_GPIO_4_5_0),
        .bt_feature_bit_map = 0,
        .ext_tcp_ip_feature_bit_map = (SL_SI91X_EXT_TCP_IP_WINDOW_DIV | SL_SI91X_CONFIG_FEAT_EXTENTION_VALID | SL_SI91X_EXT_TCP_IP_FEAT_SSL_THREE_SOCKETS | SL_SI91X_EXT_TCP_IP_WAIT_FOR_SOCKET_CLOSE),
        .ble_feature_bit_map = 0,
        .ble_ext_feature_bit_map = 0,
        .config_feature_bit_map = SL_SI91X_FEAT_SLEEP_GPIO_SEL_BITMAP},
    .ta_pool = {.tx_ratio_in_buffer_pool = 1, .rx_ratio_in_buffer_pool = 1, .global_ratio_in_buffer_pool = 1}};

static const sl_net_wifi_client_profile_t wifi_client_profile = {
    .config = {
        .ssid = {
            .value = WIUS_WIFI_SSID,
            .length = sizeof(WIUS_WIFI_SSID) - 1,
        },
        .channel = {
            .channel = SL_WIFI_AUTO_CHANNEL,
            .band = SL_WIFI_AUTO_BAND,
            .bandwidth = SL_WIFI_AUTO_BANDWIDTH,
        },
        .channel_bitmap.channel_bitmap_2_4 = SL_WIFI_DEFAULT_CHANNEL_BITMAP,
        .bssid = {{0}},
        .bss_type = SL_WIFI_BSS_TYPE_INFRASTRUCTURE,
        .security = DEFAULT_WIFI_CLIENT_SECURITY_TYPE,
        .encryption = DEFAULT_WIFI_CLIENT_ENCRYPTION_TYPE,
        .client_options = 0,
        .credential_id = SL_NET_DEFAULT_WIFI_CLIENT_CREDENTIAL_ID,
    },
    .ip = {
        .mode = SL_IP_MANAGEMENT_DHCP,
        .type = REQUIRED_IP_TYPE,
        .host_name = NULL,
        .ip = {{{0}}},
    },
};

static const sl_net_wifi_psk_credential_entry_t wifi_client_credential = {
    .type = SL_NET_WIFI_PSK,
    .data_length = sizeof(WIUS_WIFI_PASS) - 1,
    .data = WIUS_WIFI_PASS,
};

sl_status_t wius_wifi_init(void)
{
    sl_status_t status = SL_STATUS_OK;

    status = sl_net_init(SL_NET_WIFI_CLIENT_INTERFACE, &station_init_configuration, NULL, NULL);
    if (status != SL_STATUS_OK)
    {
        LOG_E("Failed to start Wi-Fi Client interface: 0x%lx", status);
        return status;
    }

    // Somehow makes initialization hang
    // sl_mac_address_t mac_addr = {0};
    // status = sl_wifi_get_mac_address(SL_WIFI_CLIENT_INTERFACE, &mac_addr);
    // if (status == SL_STATUS_OK)
    // {
    //     LOG_I("MAC: %x:%x:%x:%x:%x:%x",
    //           mac_addr.octet[0],
    //           mac_addr.octet[1],
    //           mac_addr.octet[2],
    //           mac_addr.octet[3],
    //           mac_addr.octet[4],
    //           mac_addr.octet[5]);
    // }
    // else
    // {
    //     LOG_W("Failed to get MAC address: 0x%lx", status);
    // }

    status = sl_net_set_profile(SL_NET_WIFI_CLIENT_INTERFACE, SL_NET_PROFILE_ID_1, &wifi_client_profile);
    if (status != SL_STATUS_OK)
    {
        LOG_E("Failed to set Wi-Fi client profile: 0x%lx", status);
        return status;
    }

    status = sl_net_set_credential(SL_NET_DEFAULT_WIFI_CLIENT_CREDENTIAL_ID, wifi_client_credential.type, &wifi_client_credential.data, wifi_client_credential.data_length);
    if (status != SL_STATUS_OK)
    {
        LOG_E("Failed to set Wi-Fi client credential: 0x%lx", status);
        return status;
    }

    status = sl_net_up(SL_NET_WIFI_CLIENT_INTERFACE, SL_NET_PROFILE_ID_1);
    if (status != SL_STATUS_OK)
    {
        LOG_E("Failed to bring Wi-Fi client interface up: 0x%lx", status);
        if (status == 0x10003)
        {
            LOG_E("SSID '%s' not found", WIUS_WIFI_SSID);
        }
        else if (status == 0x10008)
        {
            LOG_E("PASS '%s' not accepted", WIUS_WIFI_PASS);
        }
        return status;
    }
    LOG_D("Wi-Fi client connected");

    sl_net_wifi_client_profile_t profile = {0};
    status = sl_net_get_profile(SL_NET_WIFI_CLIENT_INTERFACE, SL_NET_PROFILE_ID_1, &profile);
    if (status == SL_STATUS_OK)
    {
        uint8_t *ip_bytes = profile.ip.ip.v4.ip_address.bytes;
        LOG_I("IP: %d.%d.%d.%d", ip_bytes[0], ip_bytes[1], ip_bytes[2], ip_bytes[3]);
    }

    return status;
}

sl_status_t wius_wifi_deinit(void)
{
    return sl_net_deinit(SL_NET_WIFI_CLIENT_INTERFACE);
}

sl_status_t wius_wifi_set_performance_profile(wius_wifi_performance_profile_t profile)
{
    sl_status_t status = SL_STATUS_OK;

    sl_wifi_performance_profile_t set_profile;

    switch (profile)
    {
    case WIUS_PERF_PROFILE_HIGHSPEED:
        set_profile.profile = HIGH_PERFORMANCE;
        break;
    case WIUS_PERF_PROFILE_LOWPOWER:
        set_profile.profile = ASSOCIATED_POWER_SAVE;
        break;
    default:
        return SL_STATUS_INVALID_PARAMETER;
    }

    CHECK_STATUS(sl_wifi_set_performance_profile(&set_profile));

    sl_wifi_performance_profile_t read_profile;
    CHECK_STATUS(sl_wifi_get_performance_profile(&read_profile));

    //	switch (read_profile.profile)
    //	{
    //	case HIGH_PERFORMANCE:
    //		LOG_D("Performance profile: HIGH_PERFORMANCE");
    //		break;
    //	case ASSOCIATED_POWER_SAVE:
    //		LOG_D("Performance profile: ASSOCIATED_POWER_SAVE");
    //		break;
    //	case ASSOCIATED_POWER_SAVE_LOW_LATENCY:
    //		LOG_D("Performance profile: ASSOCIATED_POWER_SAVE_LOW_LATENCY");
    //		break;
    //	case STANDBY_POWER_SAVE:
    //		LOG_D("Performance profile: STANDBY_POWER_SAVE");
    //		break;
    //	case STANDBY_POWER_SAVE_WITH_RAM_RETENTION:
    //		LOG_D("Performance profile: STANDBY_POWER_SAVE_WITH_RAM_RETENTION");
    //		break;
    //	default:
    //		LOG_W("Unknown performance profile");
    //	}

    if (read_profile.profile != set_profile.profile)
    {
        return SL_STATUS_SI91X_POWER_SAVE_NOT_SUPPORTED;
    }

    return status;
}
