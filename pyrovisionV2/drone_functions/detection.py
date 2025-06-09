import random

def fireDetection():
    fireDetected = random.choice([True, False])
    intensity = ""
    if fireDetected:
        intensity = random.choice(["Low", "High"])
    return fireDetected, intensity  

