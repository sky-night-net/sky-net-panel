---
description: Sky-Net development workflow — build, run, and test the panel
---

// turbo-all

## Development Commands

1. Install Python dependencies:
```bash
cd /Users/sky_night/Projects/sky-net && pip3 install flask flask-cors requests psutil bcrypt qrcode
```

2. Run the Sky-Net panel server:
```bash
cd /Users/sky_night/Projects/sky-net && python3 sky_net.py
```

3. Stop the Sky-Net panel server:
```bash
ps aux | grep sky_net.py | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null; echo "Stopped"
```

4. Run database migrations:
```bash
cd /Users/sky_night/Projects/sky-net && python3 -c "from sky_net import init_db; init_db(); print('DB initialized')"
```

5. Check server status:
```bash
curl -s http://localhost:9090/server/status | python3 -m json.tool
```

6. Create project archive:
```bash
cd /Users/sky_night/Projects && tar czf sky-net-backup.tar.gz sky-net/
```

7. SSH to test server:
```bash
sshpass -p '1q2w3e!@571' ssh -o StrictHostKeyChecking=no root@10.101.50.101
```

8. Copy files to test server:
```bash
sshpass -p '1q2w3e!@571' scp -o StrictHostKeyChecking=no -r /Users/sky_night/Projects/sky-net root@10.101.50.101:/opt/sky-net/
```

9. List project files:
```bash
find /Users/sky_night/Projects/sky-net -type f | head -50
```

10. Check Python syntax:
```bash
cd /Users/sky_night/Projects/sky-net && python3 -m py_compile sky_net.py && echo "OK"
```
