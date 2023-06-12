import os

if os.path.exists('./.dev.env'):
    MODE = "Development"
else:
    MODE = "Production"


print(MODE)