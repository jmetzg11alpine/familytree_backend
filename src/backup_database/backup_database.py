from health import save_health_data
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'health':
        save_health_data()
    elif len(sys.argv) > 1 and sys.argv[1] == 'all':
        save_health_data()

    else:
        print('add argument: health or all')
