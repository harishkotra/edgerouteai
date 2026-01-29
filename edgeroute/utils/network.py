import speedtest
import logging
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NetworkAwareness:
    def __init__(self):
        pass

    def get_network_metrics(self) -> Dict[str, float]:
        """
        Returns network metrics: download (Mbps), upload (Mbps), latency (ms).
        """
        try:
            # For speed, we might want to use a lighter check or cached value in production.
            # Here we use speedtest-cli.
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            
            # download/upload are in bits per second
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000    # Convert to Mbps
            latency = st.results.ping
            
            return {
                "download_mbps": round(download_speed, 2),
                "upload_mbps": round(upload_speed, 2),
                "latency_ms": round(latency, 2)
            }
        except Exception as e:
            logger.error(f"Failed to measure network speed: {e}")
            # Return safe defaults or indicate failure
            return {
                "download_mbps": 0.0,
                "upload_mbps": 0.0,
                "latency_ms": 999.0
            }

if __name__ == "__main__":
    na = NetworkAwareness()
    print(json.dumps(na.get_network_metrics(), indent=2))
