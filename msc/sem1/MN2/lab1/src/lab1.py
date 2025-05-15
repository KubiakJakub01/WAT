import argparse
import random


TYPE_TO_LEN_DICT = {"float": 32, "double": 64}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_type",
        type=str,
        default="float",
        choices=["float", "double"],
        help="Provide input type: float 32 bits, double 64 bits",
    )
    parser.add_argument("--input", type=str, help="Input binary number")

    def _valid_args(args):
        if args.input is None:
            args.input = generate_random_bits_string(TYPE_TO_LEN_DICT[args.input_type])
        if args.input_type == "float":
            assert len(args.input) == 32, (
                "Binary string must be 32 bits long for float type"
            )
        if args.input_type == "double":
            assert len(args.input) == 64, (
                "Binary string must be 64 bits long for double type"
            )
        return args

    return _valid_args(parser.parse_args())


def generate_random_bits_string(p):
    binary_string = ""
    for _ in range(p):
        temp = str(random.randint(0, 1))
        binary_string += temp
    return binary_string


def binary_to_float32(binary_string: str) -> float:
    if len(binary_string) != 32:
        raise ValueError("Binary string must be 32 bits long")

    sign_bit = int(binary_string[0])
    exponent_bits = binary_string[1:9]
    mantissa_bits = binary_string[9:]
    sign = (-1) ** sign_bit
    exponent = int(exponent_bits, 2) - 127
    mantissa = 1
    for i, bit in enumerate(mantissa_bits):
        mantissa += int(bit) * 2 ** -(i + 1)

    return sign * mantissa * 2**exponent


def binary_to_float64(binary_string):
    if len(binary_string) != 64:
        raise ValueError("Binary string must be 64 bits long")

    sign_bit = int(binary_string[0])
    exponent_bits = binary_string[1:12]
    mantissa_bits = binary_string[12:]
    sign = (-1) ** sign_bit
    exponent = int(exponent_bits, 2) - 1023
    mantissa = 1
    for i, bit in enumerate(mantissa_bits):
        mantissa += int(bit) * 2 ** -(i + 1)

    return sign * mantissa * 2**exponent


if __name__ == "__main__":
    args = parse_args()
    if args.input_type == "float":
        print(f"Input: {args.input}")
        print(f"Output: {binary_to_float32(args.input)}(float)")
    if args.input_type == "double":
        print(f"Input: {args.input}")
        print(f"Output: {binary_to_float64(args.input)}(double)")
