# go2rtc exporter

This is a simple tool to export go2rtc producer and consumer metrics to Prometheus.

The path to the go2rtc API comes from `GO2RTC_PATH` environment variable or first argument. Default is `http://localhost:1984/api/streams`.

Metrics port is `1985`.