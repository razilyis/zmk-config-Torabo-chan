#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(torabo_diag, LOG_LEVEL_INF);

/* Read-only diagnostics: do not replace callbacks or reconfigure scan/SPI pins. */
static void status_thread(void *a, void *b, void *c) {
    ARG_UNUSED(a);
    ARG_UNUSED(b);
    ARG_UNUSED(c);
    const struct device *sensor = DEVICE_DT_GET(DT_NODELABEL(trackball));
    const struct device *scan = DEVICE_DT_GET(DT_CHOSEN(zmk_kscan));
    const struct device *spi = DEVICE_DT_GET(DT_BUS(DT_NODELABEL(trackball)));
    const struct gpio_dt_spec irq = GPIO_DT_SPEC_GET(DT_NODELABEL(trackball), irq_gpios);
    const struct gpio_dt_spec row = GPIO_DT_SPEC_GET_BY_IDX(DT_CHOSEN(zmk_kscan), row_gpios, 0);

    while (true) {
        int motion = gpio_is_ready_dt(&irq) ? gpio_pin_get_dt(&irq) : -ENODEV;
        int row_level = gpio_is_ready_dt(&row) ? gpio_pin_get_dt(&row) : -ENODEV;
        LOG_INF("usb-diag-v1 uptime=%lldms spi_ready=%d paw_ready=%d kscan_ready=%d motion_active=%d row_sample=%d",
                (long long)k_uptime_get(), device_is_ready(spi), device_is_ready(sensor),
                device_is_ready(scan), motion, row_level);
        k_sleep(K_SECONDS(2));
    }
}

K_THREAD_DEFINE(torabo_status_thread, 1024, status_thread, NULL, NULL, NULL, 10, 0, 5000);
