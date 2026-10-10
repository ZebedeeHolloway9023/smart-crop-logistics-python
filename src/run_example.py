import argparse
import json

from logistics_crop import InfraiImageClient, ProofFile, ShipmentEvent, process_event


def main() -> None:
    parser = argparse.ArgumentParser(description="Crop a shipment proof image")
    parser.add_argument("--image", required=True, type=json.loads, help="JSON image reference for image.smart_crop")
    parser.add_argument("--filename", default="proof.jpg", help="Proof filename in the output")
    args = parser.parse_args()
    event = ShipmentEvent(
        shipment_id="SHP-2048",
        status="exception",
        exception_reason="damaged carton",
        proof=ProofFile(image=args.image, filename=args.filename),
    )
    result = process_event(event, InfraiImageClient())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
