import librosa
import numpy as np

class AudioUtils:
    @staticmethod
    def get_prosody_features(file_path: str):
        """Extract basic prosodic features: pitch and tempo."""
        try:
            y, sr = librosa.load(file_path)
            
            # 1. Pitch (Fundamental Frequency)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            avg_pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            
            # 2. Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # 3. Energy (RMS)
            rms = librosa.feature.rms(y=y)
            avg_energy = np.mean(rms)
            
            return {
                "pitch": float(avg_pitch),
                "tempo": float(tempo),
                "energy": float(avg_energy)
            }
        except Exception as e:
            print(f"Audio Analysis Error: {str(e)}")
            return None

    @staticmethod
    def classify_tone(features: dict):
        """Simple heuristic to classify tone from acoustic features."""
        if not features:
            return "Neutral"
        
        # Heuristics (calibrated values would be better)
        # High pitch + High tempo usually = Excited/Anxious
        # Low pitch + Low tempo = Sad/Tired
        
        if features["tempo"] > 140:
            return "Agitated/Excited"
        if features["tempo"] < 80 and features["energy"] < 0.01:
            return "Withdrawn/Low Energy"
        
        return "Neutral"

audio_utils = AudioUtils()
