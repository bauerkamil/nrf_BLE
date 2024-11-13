#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/sys/printk.h>
#define LED1_PIN DT_GPIO_PIN(DT_ALIAS(led0), gpios)
#define LED2_PIN DT_GPIO_PIN(DT_ALIAS(led1), gpios)
#define LED3_PIN DT_GPIO_PIN(DT_ALIAS(led2), gpios)
#define LED4_PIN DT_GPIO_PIN(DT_ALIAS(led3), gpios)

static const struct device *led_device;

// Bluetooth UUIDs
#define LED_SERVICE_UUID BT_UUID_DECLARE_128(BT_UUID_128_ENCODE(0x12345678, 0x1234, 0x1234, 0x1234, 0x1234567890AB))
#define LED_CHARACTERISTIC_UUID BT_UUID_DECLARE_128(BT_UUID_128_ENCODE(0xABCD1234, 0x5678, 0x5678, 0x5678, 0x1234567890AB))

// handle BLE
ssize_t write_led_control(struct bt_conn *conn, const struct bt_gatt_attr *attr,
                          const void *buf, uint16_t len, uint16_t offset, uint8_t flags)
{
    if (len != 1) {
        printk("Invalid command length\n");
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }

    uint8_t command = *((uint8_t *)buf);
    printk("Received command: %d\n", command);

    switch (command) {
    case 1:
        gpio_pin_set(led_device, LED1_PIN, 1);
        break;
    case 2:
        gpio_pin_set(led_device, LED2_PIN, 1);
        break;
    case 3:
        gpio_pin_set(led_device, LED3_PIN, 1);
        break;
    case 4:
        gpio_pin_set(led_device, LED4_PIN, 1);
        break;
    case 0:
        gpio_pin_set(led_device, LED1_PIN, 0);
        gpio_pin_set(led_device, LED2_PIN, 0);
        gpio_pin_set(led_device, LED3_PIN, 0);
        gpio_pin_set(led_device, LED4_PIN, 0);
        break;
    default:
        printk("Unknown command\n");
        return BT_GATT_ERR(BT_ATT_ERR_WRITE_NOT_PERMITTED);
    }

    return len;
}

// Define the GATT service and characteristic
BT_GATT_SERVICE_DEFINE(led_svc,
    BT_GATT_PRIMARY_SERVICE(LED_SERVICE_UUID),
    BT_GATT_CHARACTERISTIC(LED_CHARACTERISTIC_UUID,
                           BT_GATT_CHRC_WRITE,
                           BT_GATT_PERM_WRITE,
                           NULL, write_led_control, NULL),
);

// Initialize BLE
static void bt_ready(int err)
{
    if (err) {
        printk("Bluetooth init failed (err %d)\n", err);
        return;
    }
    printk("Bluetooth initialized\n");
}

void main(void)
{
    int err;

    // Initialize LEDs
    led_device = DEVICE_DT_GET(DT_GPIO_CTLR(DT_ALIAS(led0), gpios));
    if (!led_device) {
        printk("LED device not found\n");
        return;
    }

    gpio_pin_configure(led_device, LED1_PIN, GPIO_OUTPUT);
    gpio_pin_configure(led_device, LED2_PIN, GPIO_OUTPUT);
    gpio_pin_configure(led_device, LED3_PIN, GPIO_OUTPUT);
    gpio_pin_configure(led_device, LED4_PIN, GPIO_OUTPUT);

    // Initialize BLE
    err = bt_enable(bt_ready);
    if (err) {
        printk("Bluetooth init failed (err %d)\n", err);
        return;
    }

    printk("LED control service started\n");
}
