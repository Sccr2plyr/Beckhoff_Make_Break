import argparse
import datetime as dt
import time

from pymodbus.client import ModbusTcpClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Continuously read Modbus discrete inputs and print states."
    )
    parser.add_argument("--host", default="192.168.1.1", help="PLC IP address")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port")
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Starting discrete input address (try 0 or 8 for EL1088 mapping)",
    )
    parser.add_argument("--count", type=int, default=8, help="Number of inputs to read")
    parser.add_argument("--slave", type=int, default=1, help="Modbus unit/slave ID")
    parser.add_argument(
        "--interval",
        type=float,
        default=0.2,
        help="Seconds between reads",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan a wider address range and print changed inputs only",
    )
    parser.add_argument(
        "--scan-start",
        type=int,
        default=0,
        help="Scan range start (used with --scan)",
    )
    parser.add_argument(
        "--scan-count",
        type=int,
        default=32,
        help="How many discrete inputs to scan (used with --scan)",
    )
    return parser.parse_args()


def connect_client(host, port):
    client = ModbusTcpClient(host, port=port, timeout=5)
    ok = client.connect()
    if not ok:
        raise RuntimeError(f"Could not connect to {host}:{port}")
    return client


def read_discrete_inputs_compat(client, start, count, slave):
    # pymodbus changed naming across versions: some use `slave`, others `unit`.
    try:
        return client.read_discrete_inputs(start, count=count, slave=slave)
    except TypeError:
        try:
            return client.read_discrete_inputs(start, count=count, unit=slave)
        except TypeError:
            # Last fallback for very old signatures.
            return client.read_discrete_inputs(start, count)


def main():
    args = parse_args()

    if args.start < 0:
        raise ValueError("--start must be >= 0")
    if args.count <= 0:
        raise ValueError("--count must be > 0")
    if args.interval <= 0:
        raise ValueError("--interval must be > 0")
    if args.scan_start < 0:
        raise ValueError("--scan-start must be >= 0")
    if args.scan_count <= 0:
        raise ValueError("--scan-count must be > 0")

    client = connect_client(args.host, args.port)
    if args.scan:
        print(
            f"Connected to {args.host}:{args.port} | scanning DI {args.scan_start}..{args.scan_start + args.scan_count - 1}"
        )
    else:
        print(
            f"Connected to {args.host}:{args.port} | reading DI {args.start}..{args.start + args.count - 1}"
        )
    print("Press Ctrl+C to stop.\n")

    previous_bits = None

    try:
        while True:
            if args.scan:
                start = args.scan_start
                count = args.scan_count
            else:
                start = args.start
                count = args.count

            response = read_discrete_inputs_compat(client, start, count, args.slave)

            if response.isError():
                print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] read error: {response}")
                time.sleep(args.interval)
                continue

            bits = [bool(response.bits[i]) for i in range(count)]

            if args.scan:
                changes = []
                if previous_bits is None:
                    for i, bit in enumerate(bits):
                        if bit:
                            changes.append(f"I{start + i}=1")
                else:
                    for i, bit in enumerate(bits):
                        if bit != previous_bits[i]:
                            changes.append(f"I{start + i}={'1' if bit else '0'}")

                if changes:
                    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] change: {' '.join(changes)}")
                previous_bits = bits
            else:
                values = " ".join(f"I{start + i}={'1' if bit else '0'}" for i, bit in enumerate(bits))
                print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {values}")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        client.close()


if __name__ == "__main__":
    main()
