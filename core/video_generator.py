"""
Video Generator - Tích hợp Google Veo 3.0 qua Vertex AI
Tạo video thật từ prompt
"""
import os
import time
import base64
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime

# Google Auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request


class VideoGenerator:
    """
    Generate video using Google Veo 3.0 via Vertex AI
    """
    
    def __init__(self):
        self.credentials = None
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.region = os.getenv("VERTEX_REGION", "us-central1")
        
        # Load Service Account credentials
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        if creds_path:
            # Nếu là path relative, convert sang absolute
            if not os.path.isabs(creds_path):
                creds_path = os.path.join(os.path.dirname(__file__), "..", creds_path)
            
            if os.path.exists(creds_path):
                self.credentials = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
        
        # Veo 3.0 endpoint
        self.base_url = f"https://{self.region}-aiplatform.googleapis.com/v1"
        self.model = "veo-2.0-generate-001"  # Veo model
        
    def _get_access_token(self) -> Optional[str]:
        """Get valid access token from credentials"""
        if not self.credentials:
            return None
        
        # Refresh token if expired
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        
        return self.credentials.token
        
    def _get_endpoint(self) -> str:
        """Get Vertex AI endpoint for video generation"""
        return f"{self.base_url}/projects/{self.project_id}/locations/{self.region}/publishers/google/models/{self.model}:predictLongRunning"
    
    def _get_headers(self) -> Dict:
        """Get request headers with authentication"""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",  # TikTok format
        duration_seconds: int = 5,
        output_path: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate video from text prompt using Veo 3.0
        
        Args:
            prompt: Visual prompt for video generation
            aspect_ratio: "9:16" for TikTok, "16:9" for YouTube
            duration_seconds: Video duration (5-60 seconds)
            output_path: Path to save video file
            
        Returns:
            Tuple (success, message, video_path)
        """
        if not self.credentials:
            return False, "Thiếu GOOGLE_APPLICATION_CREDENTIALS trong .env", None
        
        if not self.project_id:
            return False, "Thiếu GOOGLE_CLOUD_PROJECT trong .env", None
        
        try:
            # Prepare request payload
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "aspectRatio": aspect_ratio,
                    "durationSeconds": duration_seconds,
                    "personGeneration": "allow_adult",
                    "sampleCount": 1
                }
            }
            
            # Start video generation (async operation)
            response = requests.post(
                self._get_endpoint(),
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                return False, f"API Error: {error_msg}", None
            
            # Get operation name for polling
            operation = response.json()
            operation_name = operation.get("name")
            
            if not operation_name:
                return False, "Không nhận được operation ID", None
            
            # Poll for completion
            video_data = self._poll_operation(operation_name)
            
            if not video_data:
                return False, "Timeout hoặc lỗi khi tạo video", None
            
            # Save video
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"outputs/video_{timestamp}.mp4"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Decode and save video
            video_bytes = base64.b64decode(video_data)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            
            return True, "Video đã được tạo thành công!", output_path
            
        except requests.exceptions.Timeout:
            return False, "Request timeout - thử lại sau", None
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}", None
        except Exception as e:
            return False, f"Lỗi: {str(e)}", None
    
    def _poll_operation(self, operation_name: str, max_wait: int = 300) -> Optional[str]:
        """
        Poll long-running operation until completion
        
        Args:
            operation_name: Operation ID to poll
            max_wait: Maximum wait time in seconds
            
        Returns:
            Base64 encoded video data or None
        """
        poll_url = f"{self.base_url}/{operation_name}"
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    poll_url,
                    headers=self._get_headers(),
                    timeout=30
                )
                
                if response.status_code != 200:
                    time.sleep(5)
                    continue
                
                result = response.json()
                
                # Check if done
                if result.get("done"):
                    # Check for error
                    if "error" in result:
                        print(f"Operation error: {result['error']}")
                        return None
                    
                    # Get video data
                    predictions = result.get("response", {}).get("predictions", [])
                    if predictions:
                        return predictions[0].get("video", {}).get("bytesBase64Encoded")
                    return None
                
                # Still processing, wait and retry
                time.sleep(10)
                
            except Exception as e:
                print(f"Poll error: {e}")
                time.sleep(5)
        
        return None  # Timeout
    
    def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        aspect_ratio: str = "9:16",
        duration_seconds: int = 5,
        output_path: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Generate video from image + prompt (Image-to-Video)
        
        Args:
            image_path: Path to input image
            prompt: Motion/action prompt
            aspect_ratio: Output aspect ratio
            duration_seconds: Video duration
            output_path: Path to save video
            
        Returns:
            Tuple (success, message, video_path)
        """
        if not self.credentials or not self.project_id:
            return False, "Thiếu API credentials", None
        
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", 
                ".png": "image/png",
                ".webp": "image/webp"
            }.get(ext, "image/jpeg")
            
            # Prepare payload with image
            payload = {
                "instances": [
                    {
                        "prompt": prompt,
                        "image": {
                            "bytesBase64Encoded": image_b64,
                            "mimeType": mime_type
                        }
                    }
                ],
                "parameters": {
                    "aspectRatio": aspect_ratio,
                    "durationSeconds": duration_seconds,
                    "sampleCount": 1
                }
            }
            
            # Call API
            response = requests.post(
                self._get_endpoint(),
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", response.text)
                return False, f"API Error: {error_msg}", None
            
            operation = response.json()
            operation_name = operation.get("name")
            
            if not operation_name:
                return False, "Không nhận được operation ID", None
            
            # Poll for completion
            video_data = self._poll_operation(operation_name)
            
            if not video_data:
                return False, "Timeout hoặc lỗi khi tạo video", None
            
            # Save video
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"outputs/video_{timestamp}.mp4"
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            video_bytes = base64.b64decode(video_data)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            
            return True, "Video đã được tạo thành công!", output_path
            
        except Exception as e:
            return False, f"Lỗi: {str(e)}", None


# Test function
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    generator = VideoGenerator()
    
    test_prompt = """
    Cận cảnh nhẫn kim cương lấp lánh trên nền nhung đen.
    Camera quay chậm 360 độ, ánh sáng studio chiếu vào kim cương tạo hiệu ứng cầu vồng.
    Phong cách sang trọng, cinematic.
    """
    
    success, message, path = generator.generate_video(
        prompt=test_prompt,
        aspect_ratio="9:16",
        duration_seconds=5
    )
    
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Path: {path}")
