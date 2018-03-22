#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def _validate(_stdout, _input, _output, info):
    info("comparing %s to %s" % (_stdout, _output))
    linenumber = 0
    with open(_output, "rt") as f_output:
        with open(_stdout, "rt") as f_stdout:
            for expected in f_output:
                linenumber += 1
                expected = expected.rstrip()
                found = f_stdout.readline().rstrip()
                if not expected == found:
                    info("line %d: expected %r, found %r" % (linenumber, expected, found))
                    return 0
    return 1


def validate(_stdout, _input, _output, info):
    try:
        return _validate(_stdout, _input, _output, info)

    except:
        info("some exception happened.")
        return 0


#######

if __name__ == "__main__":
    import sys
    score = validate( sys.argv[1], sys.argv[2], sys.argv[3], print )
    print("score", score)
