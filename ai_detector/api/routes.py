"""API route handlers"""

from fastapi import UploadFile, HTTPException
from typing import List
import tempfile
import os
from pathlib import Path
import time
import cv2
import numpy as np

from ..config import (
    SUPPORTED_IMAGE_FORMATS, SUPPORTED_VIDEO_FORMATS,
    MAX_IMAGE_SIZE, MAX_VIDEO_SIZE, VIDEO_FRAME_SAMPLE_RATE,
    MAX_FRAMES_TO_ANALYZE
)
from ..analyzers.watermark import WatermarkDetector
from ..analyzers.metadata import MetadataAnalyzer
from ..analyzers.frequency import FrequencyAnalyzer
from ..analyzers.noise import NoiseAnalyzer
from ..analyzers.color import ColorAnalyzer
from ..analyzers.geometry import GeometryAnalyzer
from ..analyzers.video_temporal import VideoTemporalAnalyzer
from ..analyzers.video_motion import VideoMotionAnalyzer
from ..decision.scorer import DecisionEngine
from ..utils.image_utils import load_image


async def analyze_media(file: UploadFile, fast_mode: bool = False):
    """Tek dosya analizi"""
    start_time = time.time()
    
    # Dosya uzantısı kontrolü
    file_ext = Path(file.filename).suffix.lower()
    
    is_video = file_ext in SUPPORTED_VIDEO_FORMATS
    is_image = file_ext in SUPPORTED_IMAGE_FORMATS
    
    if not (is_video or is_image):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {SUPPORTED_IMAGE_FORMATS + SUPPORTED_VIDEO_FORMATS}"
        )
    
    # Geçici dosyaya kaydet
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
        content = await file.read()
        
        # Boyut kontrolü
        if is_image and len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image too large (max 50MB)")
        if is_video and len(content) > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail="Video too large (max 500MB)")
        
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        if is_video:
            result = analyze_video_file(tmp_path, fast_mode)
        else:
            result = analyze_image_file(tmp_path, fast_mode)
        
        processing_time = (time.time() - start_time) * 1000  # ms
        result['processing_time_ms'] = round(processing_time, 2)
        result['filename'] = file.filename
        
        return result
        
    finally:
        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def convert_to_native_types(obj):
    """NumPy ve diğer tipleri Python native tiplerine çevir"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def analyze_image_file(file_path: str, fast_mode: bool = False):
    """Görüntü dosyası analizi"""
    try:
        # Load image
        image = load_image(file_path)
        
        # Decision engine
        engine = DecisionEngine()
        
        # 1. Metadata & Watermark (ÖNCELİK #1)
        metadata_analyzer = MetadataAnalyzer()
        metadata_result = metadata_analyzer.analyze(file_path, is_video=False)
        
        if metadata_result.get('c2pa_synthetic', False):
            engine.add_detection('c2pa_synthetic', True, "C2PA metadata indicates synthetic origin")
        
        if metadata_result.get('metadata_suspicious', False):
            engine.add_detection('metadata_suspicious', True, "Suspicious metadata patterns")
        
        # Watermark detection
        watermark_detector = WatermarkDetector()
        watermark_result = watermark_detector.analyze(image)
        
        if watermark_result.get('watermark_detected', False):
            engine.add_detection('watermark_detected', True, 
                               f"Watermark detected: {', '.join(watermark_result.get('detections', []))}")
        
        # 2. Frequency Analysis
        freq_analyzer = FrequencyAnalyzer()
        freq_result = freq_analyzer.analyze(image)
        
        if freq_result.get('freq_ratio_anomaly', False):
            engine.add_detection('freq_ratio_anomaly', True, "DCT frequency ratio anomaly")
        
        if freq_result.get('checkerboard_pattern', False):
            engine.add_detection('checkboard_pattern', True, "Diffusion checkerboard pattern detected")
        
        # 3. Noise Analysis (skip in fast mode)
        noise_result = {}
        if not fast_mode:
            noise_analyzer = NoiseAnalyzer()
            noise_result = noise_analyzer.analyze(image)
            
            if noise_result.get('noise_variance_low', False):
                engine.add_detection('noise_variance_low', True, "Unnaturally low noise variance")
        
        # 4. Color Analysis
        color_analyzer = ColorAnalyzer()
        color_result = color_analyzer.analyze(image)
        
        if color_result.get('rgb_correlation_high', False):
            engine.add_detection('rgb_correlation_high', True, "Abnormally high RGB channel correlation")
        
        # 5. Geometry Analysis (skip in fast mode)
        geom_result = {}
        if not fast_mode:
            geom_analyzer = GeometryAnalyzer()
            geom_result = geom_analyzer.analyze(image)
            
            if geom_result.get('edge_fragmented', False):
                engine.add_detection('edge_fragmented', True, "Fragmented edge patterns")
        
        # Calculate verdict
        verdict_data = engine.calculate_verdict()
        
        result = {
            'verdict': verdict_data['verdict'],
            'confidence': verdict_data['confidence'],
            'total_score': verdict_data['total_score'],
            'scores': verdict_data['scores'],
            'evidence': verdict_data['evidence'],
            'analysis_details': {
                'metadata': metadata_result,
                'watermark': watermark_result,
                'frequency': freq_result,
                'color': color_result
            }
        }
        
        # Convert all numpy types to native Python types
        return convert_to_native_types(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def analyze_video_file(file_path: str, fast_mode: bool = False):
    """Video dosyası analizi"""
    try:
        # Video metadata
        metadata_analyzer = MetadataAnalyzer()
        metadata_result = metadata_analyzer.analyze(file_path, is_video=True)
        
        # Decision engine
        engine = DecisionEngine()
        
        if metadata_result.get('metadata_suspicious', False):
            engine.add_detection('metadata_suspicious', True, "Suspicious video metadata")
        
        # Extract frames
        cap = cv2.VideoCapture(file_path)
        frames = []
        frame_count = 0
        
        while len(frames) < MAX_FRAMES_TO_ANALYZE:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Sample every Nth frame
            if frame_count % VIDEO_FRAME_SAMPLE_RATE == 0:
                # BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            
            frame_count += 1
        
        cap.release()
        
        if len(frames) == 0:
            raise HTTPException(status_code=400, detail="Could not extract frames from video")
        
        # Analyze first frame (image tests)
        first_frame = frames[0]
        
        # Watermark
        watermark_detector = WatermarkDetector()
        watermark_result = watermark_detector.analyze(first_frame)
        
        if watermark_result.get('watermark_detected', False):
            engine.add_detection('watermark_detected', True, "Video watermark detected")
        
        # Frequency (first frame)
        freq_analyzer = FrequencyAnalyzer()
        freq_result = freq_analyzer.analyze(first_frame)
        
        if freq_result.get('checkerboard_pattern', False):
            engine.add_detection('checkboard_pattern', True, "Diffusion artifacts in video frames")
        
        # Temporal analysis
        temporal_result = {}
        if len(frames) >= 2:
            temporal_analyzer = VideoTemporalAnalyzer()
            temporal_result = temporal_analyzer.analyze(frames)
            
            if temporal_result.get('temporal_flicker', False):
                engine.add_detection('temporal_flicker', True, "Diffusion flicker detected")
        
        # Motion analysis (skip in fast mode)
        motion_result = {}
        if not fast_mode and len(frames) >= 2:
            motion_analyzer = VideoMotionAnalyzer()
            motion_result = motion_analyzer.analyze(frames)
            
            if motion_result.get('motion_vector_irregular', False):
                engine.add_detection('motion_vector_irregular', True, "Irregular motion vectors")
        
        # Calculate verdict
        verdict_data = engine.calculate_verdict()
        
        result = {
            'verdict': verdict_data['verdict'],
            'confidence': verdict_data['confidence'],
            'total_score': verdict_data['total_score'],
            'scores': verdict_data['scores'],
            'evidence': verdict_data['evidence'],
            'frames_analyzed': len(frames),
            'analysis_details': {
                'metadata': metadata_result,
                'watermark': watermark_result
            }
        }
        
        # Convert all numpy types to native Python types
        return convert_to_native_types(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")


async def analyze_batch(files: List[UploadFile]):
    """Batch analiz"""
    results = []
    
    for file in files:
        try:
            result = await analyze_media(file, fast_mode=True)
            results.append(result)
        except Exception as e:
            results.append({
                'filename': file.filename,
                'error': str(e),
                'verdict': 'ERROR'
            })
    
    return {'results': results, 'total': len(results)}


def health_check():
    """Health check"""
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'supported_formats': {
            'images': SUPPORTED_IMAGE_FORMATS,
            'videos': SUPPORTED_VIDEO_FORMATS
        }
    }
