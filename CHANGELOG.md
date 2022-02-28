# HalfAPI

## 0.6.8

- Fix testing lib for domains (add default secret and debug option)

## 0.6.2

- Domains now need to include the following variables in their __init__.py
    - __name__ (str, optional)
    - __id__ (str, optional)
- halfapi domain


## 0.1.0

- Mounts domain routers with their ACLs as decorator
- Configuration example files for systemd and a system-wide halfapi install
- Runs projects
- Handles JWT authentication middleware
