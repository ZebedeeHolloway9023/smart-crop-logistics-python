from logistics_crop import ProofFile, ShipmentEvent, process_event


class RecordingClient:
    def __init__(self):
        self.calls = []

    def smart_crop(self, image, aspect):
        self.calls.append((image, aspect))
        return {"url": f"cropped:{aspect}"}


def test_exception_event_adds_dashboard_crop():
    client = RecordingClient()
    event = ShipmentEvent("SHP-1", "exception", ProofFile("img-1", "pod.jpg"), "wet carton")
    result = process_event(event, client)
    assert set(result["crops"]) == {"label", "mobile", "dashboard"}
    assert [aspect for _, aspect in client.calls] == ["1:1", "4:5", "16:9"]
