# Locket Gold Local Activator (No Telegram Middleman)

Công cụ này đã được refactor để chạy **trực tiếp trên máy cá nhân** bằng terminal/CLI thay vì qua Telegram bot.

## Những gì mới

- Chạy local bằng `./run.sh`.
- Có **hệ thống queue + worker pool** giống bot cũ (`NUM_WORKERS`).
- Giữ nguyên logic lõi:
  - resolve username/link -> UID
  - inject receipt RevenueCat
  - tạo profile NextDNS chống revoke
- Có GitHub Action build file `.exe` và upload artifact.

## Chạy trực tiếp trên máy (Linux/macOS)

```bash
chmod +x run.sh
./run.sh
```

Sau khi chạy, dùng các lệnh:

- `activate <username_hoặc_link_locket>`
- `queue`
- `stats`
- `setlang VI` hoặc `setlang EN`
- `help`
- `exit`

## Cấu hình

Sửa `app/config.py`:

- `NEXTDNS_KEY`
- `TOKEN_SETS` (fetch_token/app_transaction/hash)
- `NUM_WORKERS`

## Build EXE bằng GitHub Actions

Workflow: `.github/workflows/build-exe.yml`

- Khi push/PR/manual trigger, action sẽ:
  1. cài Python + dependencies
  2. build bằng PyInstaller (`--onefile`)
  3. upload artifact `locket-local-activator-windows`

Tải `.exe` tại tab **Actions** -> run tương ứng -> **Artifacts**.

## Lưu ý

- `.exe` build trên Windows runner, chạy trực tiếp trên Windows.
- Cần điền token thật trong `app/config.py` trước khi sử dụng thực tế.
