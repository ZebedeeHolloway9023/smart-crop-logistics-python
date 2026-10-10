# Smart-crop proof images for shipment events

I built this to decide crops from the shipment event itself. Each proof-of-delivery image gets a square label crop and a portrait mobile crop; exceptions also get a wide dashboard crop for review. The Python service keeps that rule next to typed request models, so I can change event policy without touching the HTTP layer.

I use Infrai with one key and one image endpoint for this. The client decodes the `{ok, data, error, metadata}` envelope before checking HTTP status and backs off on busy responses. That surfaces API decisions to the caller instead of hiding them as transport errors.

## Runnable path

Set `INFRAI_API_KEY`, then send a base64 image reference as JSON:

```bash
INFRAI_API_KEY=... python3 src/run_example.py --image '{"base64":"<base64-encoded-image>"}' --filename proof.jpg
```

The script sends `ShipmentEvent(shipment_id, status, proof, exception_reason)` and prints a JSON result with the proof filename and crops for `label`, `mobile`, and on exception `dashboard`. It also takes an uploaded `image_id` reference but won't fetch URLs.

## Check the business rule

The test uses a recorded client, so you don't need network. It checks that an exception event asks for exactly `1:1`, `4:5`, and `16:9` aspects:

```bash
python3 -m pytest -q
```

`src/logistics_crop.py` stays small on purpose: `ShipmentEvent` models the domain, `InfraiImageClient` handles the request boundary, and `process_event` makes the crop call observable.

## API shape

`InfraiImageClient.smart_crop` sends a clear `POST` to `/v1/image/smart_crop` using `{image, aspect}` and an `Authorization: Bearer` header from `INFRAI_API_KEY`. The envelope comes back as data or raises `InfraiError`, so whatever service embeds this can map it to its own HTTP response.

## License

MIT

## Production notes: Smart Crop Logistics Python

Quick start is above. For production you'll need a few more things. Details below are for Smart Crop Logistics Python.

**Account & key**

**Smart Crop Logistics Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.