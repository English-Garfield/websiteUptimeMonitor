import logging as lg


# Configure logging
lg.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=lg.INFO,
    handlers=[
        lg.FileHandler('uptimeMonitor.log'),
        lg.StreamHandler()
    ]
)

def main():
    pass


if __name__ == "__main__":
    main()