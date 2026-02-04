import json
import os
import time
from api_client import APIClient
from rate_limiter import RateLimiter
from config import TOTAL_DEVICES, BATCH_SIZE, RATE_LIMIT_SECONDS, OUTPUT_DIR, OUTPUT_FILENAME


def generate_serial_numbers(count):
    serial_numbers = []
    for i in range(count):
        serial_numbers.append(f"SN-{i:03d}")
    return serial_numbers


def create_batches(items, batch_size):
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


def fetch_all_data(api_client, rate_limiter, serial_numbers, batch_size):
    batches = create_batches(serial_numbers, batch_size) #50
    total_batches = len(batches) #500

    print(f"Created {total_batches} batches of {batch_size} devices each")

    all_results = []
    start_time = time.time()

    for batch_num, batch in enumerate(batches, 1):
        rate_limiter.wait()

        print(
            f"Fetching batch {batch_num}/{total_batches} "
            f"({len(batch)} devices)...",
            end=" "
        )

        try:
            response = api_client.fetch_devices(batch)
            devices_data = response.get("data", [])
            all_results.extend(devices_data)
            print(f"Success ({len(all_results)}/{len(serial_numbers)} devices collected)")

        except Exception as e:
            print(f"Failed: {e}")

    elapsed_time = time.time() - start_time
    print(f"\nTotal time: {elapsed_time:.2f} seconds")
    print(f"Successfully fetched data for {len(all_results)}/{len(serial_numbers)} devices")

    return all_results


def save_results(data, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    output = {
        "total_devices": len(data),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "devices": data
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")


def generate_summary(data):
    online = sum(1 for d in data if d.get("status") == "Online")
    offline = len(data) - online

    total_power = sum(float(d.get("power", "0 kW").split()[0]) for d in data)
    avg_power = total_power / len(data) if data else 0

    return {
        "total_devices": len(data),
        "online": online,
        "offline": offline,
        "average_power_kw": round(avg_power, 2),
        "total_power_kw": round(total_power, 2)
    }


def main():
    print("=" * 60)
    print("EnergyGrid Data Aggregator")
    print("=" * 60)
    print(f"Target: {TOTAL_DEVICES} devices")
    print(f"Batch size: {BATCH_SIZE} devices per request")
    print(f"Rate limit: 1 request every {RATE_LIMIT_SECONDS} seconds")
    print("=" * 60)

    print("\nInitializing")
    api_client = APIClient()
    rate_limiter = RateLimiter(RATE_LIMIT_SECONDS)

    print("\nTesting API connection")
    rate_limiter.wait()
    if not api_client.test_connection():
        print("Failed to connect to API")
        return

    print(f"\nGenerating {TOTAL_DEVICES} serial numbers")
    serial_numbers = generate_serial_numbers(TOTAL_DEVICES) # generate serial numbers for all devices
    print(f"Generated {serial_numbers[0]} to {serial_numbers[-1]}")

    print("\nStarting data collection")
    print(f"Estimated time: {(TOTAL_DEVICES / BATCH_SIZE) * RATE_LIMIT_SECONDS:.0f} seconds\n")

    all_data = fetch_all_data(
        api_client=api_client,
        rate_limiter=rate_limiter,
        serial_numbers=serial_numbers,
        batch_size=BATCH_SIZE
    )

    print("\nGenerating summary")
    summary = generate_summary(all_data)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, v in summary.items():
        print(f"{k.replace('_', ' ').title()}: {v}")
    print("=" * 60)

    print("\nSaving results")
    save_results(all_data, OUTPUT_DIR, OUTPUT_FILENAME)

    print("\nData aggregation complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
