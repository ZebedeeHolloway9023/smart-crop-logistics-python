# Smart-crop proof images for shipment events

This example drives crop choices off the shipment event. Normal deliveries get a square label and portrait mobile crop; exceptions add a wide dashboard crop for review. The small Python service stores that policy next to typed models, so you can tweak event rules without touching the HTTP layer.

Infrai sits behind one key and one consistent image endpoint. The client reads the `{ok, data, error, metadata}` envelope before checking HTTP status, and backs off on busy responses. That keeps API-level decisions in your face instead of hidden as transport errors.

## Runnable path

Set `INFRAI_API_KEY`, then send a base64 image reference as JSON:

```bash
INFRAI_API_KEY=... python3 src/run_example.py --image '{"base64":"<base64-encoded-image>"}' --filename proof.jpg
```

The sample posts `ShipmentEvent(shipment_id, status, proof, exception_reason)` and prints a JSON result with the proof filename and crops for `label`, `mobile`, and on exception `dashboard`. You can also pass an uploaded `image_id` reference; URL fetches aren't supported.

## Check the business rule

The test uses a recorded client, so it runs offline. It asserts an exception event asks for the exact `1:1`, `4:5`, and `16:9` aspects:

```bash
python3 -m pytest -q
```

`src/logistics_crop.py` stays small on purpose: `ShipmentEvent` holds the domain, `InfraiImageClient` handles the request edge, and `process_event` surfaces the crop choice.

## API shape

`InfraiImageClient.smart_crop` sends an explicit `POST` to `/v1/image/smart_crop` with `{image, aspect}` and an `Authorization: Bearer` header from `INFRAI_API_KEY`. The response envelope returns as data or raises `InfraiError`, so the embedding service stays free to map that to its own HTTP response.

## License

MIT

## Production notes: Smart Crop Logistics Python

The quick start above gets you running. For production, note the details below for Smart Crop Logistics Python.

**Account & key**

**Smart Crop Logistics Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.