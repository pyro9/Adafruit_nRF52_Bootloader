import os
import shutil
import sys
import subprocess
import time

subprocess.run("rm -rf _build*", shell=True)
subprocess.run("rm -rf bin/*", shell=True)

travis = False
if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
    travis = True

exit_status = 0

all_boards = []
for entry in os.scandir("src/boards"):
    all_boards.append(entry.name)

#sha, version = build_info.get_version_info()

total_time = time.monotonic()

for board in all_boards:
    bin_directory = "bin/{}/".format(board)
    os.makedirs(bin_directory, exist_ok=True)

    start_time = time.monotonic()
    make_result = subprocess.run("make -j 4 BOARD={} combinehex genpkg".format(board), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    build_duration = time.monotonic() - start_time
    success = "\033[32msucceeded\033[0m"
    if make_result.returncode != 0:
        exit_status = make_result.returncode
        success = "\033[31mfailed\033[0m"

    for entry in os.scandir("_build-{}".format(board)):
        for extension in ["zip", "hex"]:
            if entry.name.endswith(extension) and "nosd" not in entry.name:
                shutil.copy(entry.path, bin_directory)

    if travis:
        print('travis_fold:start:build-{}\\r'.format(board))
    print("Build {} took {:.2f}s and {}".format(board, build_duration, success))
    if make_result.returncode != 0:
        print(make_result.stdout.decode("utf-8"))
    if travis:
        print('travis_fold:end:build-{}\\r'.format(board))

    print()

total_time = time.monotonic() - total_time
print("Total build time took {:.2f}s".format(total_time))

sys.exit(exit_status)
