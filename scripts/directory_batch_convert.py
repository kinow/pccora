import os
import sys
import re
from pathlib import Path

import logging
import argparse

from convert2netcdf4 import parseandconvert

parser = argparse.ArgumentParser(description='Recursively batch convert Vaisala old-binary format to NetCDF files. Keeps directory structure.')
parser.add_argument('--from', dest='fromdir', help='Input directory', required=True)
parser.add_argument('--to', dest='todir', help='Output directory. Created if not exists. Files will be overwritten.', required=True)

EXTENSION_REGEX = r'.*\.edt$|.*\.[0-9]{2}e$'

FORMAT = '%(asctime)s %(message)s'
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(FORMAT)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# python directory_batch_convert.py --from ~/Desktop/INVRCRGL/ --to ~/Desktop/output/ > ~/Desktop/pccora.log 2> ~/Desktop/errors.log

def main():
    try:
        process()
    except KeyboardInterrupt:
        logging.info("User canceled execution! Bye")
        sys.exit(1)

def process():
    args = parser.parse_args()

    from_dir = Path(args.fromdir)
    to_dir = Path(args.todir)

    total_files = 0
    total_success = 0
    total_error = 0
    failed_to_process = []

    for dirpath, dirnames, files in os.walk(from_dir.as_posix()):
        for name in files:
            #if name.lower().endswith(extension):
            if re.match(EXTENSION_REGEX, name.lower(), re.M|re.I):
                total_files = total_files + 1
                input_file = os.path.join(dirpath, name)
                input_path = Path(input_file)

                diff = input_path.relative_to(from_dir)
                output_path = to_dir.joinpath(diff)
                extension = output_path.suffix
                output_file = output_path.as_posix()
                output_file = output_file.replace(extension, '.nc')

                if not output_path.parent.exists():
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                if output_path.exists():
                    logger.warning("Skipping existing file [%s]" % output_file)
                    continue

                statinfo = os.stat(input_file)
                if statinfo.st_size == 0:
                    logger.warning("Skipping zero byte file [%s]" % output_file)
                    continue

                #print(output_file)
                try:
                    parseandconvert(input_file, output_file)
                    total_success = total_success + 1
                    logger.info("Successfully parsed [%s]" % output_file)
                except KeyboardInterrupt:
                    raise
                except:
                    total_error = total_error + 1
                    failed_to_process.append(output_file)
                    e = sys.exc_info()[0]
                    logger.error("Error parsing [%s]: %s" % (output_file, e))

    logger.info("### Stats ###")
    logger.info("- TOTAL   %d" % total_files)
    logger.info("- OK      %d" % total_success)
    logger.info("- NOK     %d" % total_error)
    logger.info("")
    if len(failed_to_process) > 0:
        logger.warning("## LIST OF FILES WITH PARSING ERRORS ##")
        for file in failed_to_process:
            logger.warning("- %s" % file)
    else:
        logger.info("All files parsed successfully!")


if __name__ == '__main__':
    main()

    sys.exit(0)