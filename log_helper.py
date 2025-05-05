import logging
import argparse
import inspect as ins

def setup_logging():
    """
    Sets up logging based on the --LOG-LEVEL command-line argument.
    Default log level is INFO.
    """
    parser = argparse.ArgumentParser(description="Set logging level.")
    parser.add_argument(
        "--LOG-LEVEL",
        type=str,
        default="INFO",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO."
    )
    args, unknown = parser.parse_known_args()

    log_level = getattr(logging, args.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(module)s] %(message)s"
    )

class LogHelper():

    @staticmethod
    def inspect(obj, max_depth=3, depth=0):
        """
        再帰的にオブジェクトの属性を出力する関数。

        :param obj: 調査対象のオブジェクト
        :param depth: 現在の再帰の深さ
        :param max_depth: 再帰の最大深さ
        """
        if depth > max_depth:
            print("  " * depth + f"[Max depth reached]")
            return

        print("  " * depth + f"Type: {type(obj)}")
        print("  " * depth + "Attributes and values:")

        for name, value in ins.getmembers(obj):
            if not name.startswith('__') and not ins.ismethod(value) and not ins.isfunction(value):
                print("  " * depth + f"  {name}: {value}")
                # 再帰的に子要素を辿る
                if hasattr(value, '__dict__') or isinstance(value, (list, dict, tuple)):
                    print("  " * depth + f"  {name} (nested):")
                    LogHelper.inspect(value, max_depth, depth + 1)

# Automatically set up logging when the module is imported
setup_logging()