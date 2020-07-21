# Besu private network monitor service

## Quick start:

1. Install `Python3`

2. Copy `besu-network-monitor.service` systemd service file to `/etc/systemd/system/` and make sure it has execute permission.
  ```
  cp besu-network-monitor.service /etc/systemd/system/
  ```

3. Start the monitor service:
  ```
  service besu-network-monitor start
  ```
  
  You can also run the `quickstart` shell script.
