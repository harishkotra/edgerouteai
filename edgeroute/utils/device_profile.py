import psutil
import shutil
import json
import logging
from typing import Dict, Any, List
import subprocess

logger = logging.getLogger(__name__)

class DeviceProfile:
    def __init__(self):
        pass

    def get_cpu_info(self) -> Dict[str, Any]:
        return {
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "cpu_count_physical": psutil.cpu_count(logical=False),
            "cpu_freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "cpu_percent": psutil.cpu_percent(interval=1)
        }

    def get_memory_info(self) -> Dict[str, Any]:
        vm = psutil.virtual_memory()
        return {
            "total_gb": round(vm.total / (1024**3), 2),
            "available_gb": round(vm.available / (1024**3), 2),
            "percent_used": vm.percent
        }

    def get_gpu_info(self) -> bool:
        # Simplistic check for GPU availability (Mac M-series usually have "GPU" integrated, but this checks for dedicated typically or CUDA)
        # For Mac specifically, we might assume MPS is available if it's ARM64, but let's stick to a generic check or a placeholder.
        # Since the prompt asks "GPU present", we can try to run standard commands like nvidia-smi or check for mps availability via python if we wanted to be fancy.
        # For now, we will return False as default or try to check for 'system_profiler' on Mac.
        
        # Check for Apple Silicon
        import platform
        if platform.system() == "Darwin" and platform.machine() == "arm64":
             return True # Apple Silicon has unified GPU
        
        if shutil.which("nvidia-smi"):
            return True
            
        return False

    def get_local_models(self) -> List[str]:
        # Uses ollama list
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Skip header
                if len(lines) > 0 and "NAME" in lines[0]:
                    lines = lines[1:]
                models = [line.split()[0] for line in lines if line.strip()]
                # Filter out embedding models
                models = [m for m in models if "embed" not in m]
                return models
            else:
                logger.error("Failed to list ollama models")
                return []
        except FileNotFoundError:
            logger.error("Ollama CLI not found")
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def get_profile(self) -> Dict[str, Any]:
        return {
            "ram_gb": self.get_memory_info()["total_gb"],
            "free_ram_gb": self.get_memory_info()["available_gb"],
            "cpu_cores": self.get_cpu_info()["cpu_count_logical"],
            "gpu": self.get_gpu_info(),
            "local_models": self.get_local_models()
        }

if __name__ == "__main__":
    dp = DeviceProfile()
    print(json.dumps(dp.get_profile(), indent=2))
