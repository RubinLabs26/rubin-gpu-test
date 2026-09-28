#!/usr/bin/env fish

set -l raw_script https://gist.githubusercontent.com/itzlalpekhlua/d3f580ddf4b5aaa677e77a2f7abda3ba/raw/gpu_test.py
set -l python_cmd python3
if not command -q $python_cmd
    set python_cmd python
end
if not command -q $python_cmd
    echo "Python 3 is required. Install it with: sudo pacman -S python" >&2
    exit 1
end
if not command -q curl
    echo "curl is required. Install it with: sudo pacman -S curl" >&2
    exit 1
end

set -l temp_script (mktemp -t rubin-gpu-test.XXXXXX.py)
curl --fail --location --silent --show-error $raw_script --output $temp_script
if test -r /dev/tty
    $python_cmd $temp_script $argv </dev/tty
else
    $python_cmd $temp_script $argv
end
set -l status_code $status
rm -f $temp_script
exit $status_code
