"""
    Program will be invoked by cron.  The appropriate switch will activate a TUI
    for reviewing and editing alerts.


"""
import Controller
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interface', help='interactive alert management')
    args = parser.parse_args()
    controller = Controller.Controller('test.db')
    if args.interface:
        import tui
        tui = tui.Tui(controller)
        tui.mainloop()
    else:
        controller.check_sales()


if __name__ == "__main__":
    main()
