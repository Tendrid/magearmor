import logging

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

debug_handler = logging.FileHandler("logs/mage-debug.log")
debug_handler.setFormatter(formatter)
debug_log = logging.getLogger("debug")
debug_log.setLevel(logging.DEBUG)
debug_log.addHandler(debug_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_log = logging.getLogger("info")
console_log.setLevel(logging.INFO)
console_log.addHandler(console_handler)
